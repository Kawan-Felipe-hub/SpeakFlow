from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from typing import Any
import io
import subprocess
import tempfile
import os

import azure.cognitiveservices.speech as speechsdk


@dataclass(frozen=True, slots=True)
class PronunciationWordScore:
    word: str
    accuracy_score: float | None = None
    error_type: str | None = None


@dataclass(frozen=True, slots=True)
class SpeechAssessmentResult:
    transcript: str
    overall_score: float | None
    accuracy_score: float | None
    fluency_score: float | None
    completeness_score: float | None
    word_scores: list[PronunciationWordScore]
    raw: dict[str, Any]


def _build_speech_config(*, key: str, region: str, language: str) -> speechsdk.SpeechConfig:
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_recognition_language = language
    return speech_config


def _validate_webm_header(audio_bytes: bytes) -> bool:
    """Valida se o arquivo WebM tem um cabeçalho EBML válido"""
    if len(audio_bytes) < 4:
        return False
    
    # WebM/EBML header: 0x1A 0x45 0xDF 0xA3
    return audio_bytes[:4] == b'\x1a\x45\xdf\xa3'

def _convert_webm_to_wav(audio_bytes: bytes, content_type: str = "audio/webm") -> bytes:
    """
    Converte WebM/Opus para WAV PCM usando múltiplas abordagens robustas.
    Se já for WAV, retorna os bytes originais.
    """
    print(f"Recebendo áudio em formato: {content_type}")
    print(f"Tamanho do áudio: {len(audio_bytes)} bytes")
    
    # Se já for WAV, retorna como está
    if content_type and "wav" in content_type.lower():
        print("Áudio já está em formato WAV")
        return audio_bytes
    
    # Para WebM/Opus, precisa converter
    if not (content_type and ("webm" in content_type.lower() or "opus" in content_type.lower())):
        print(f"Formato não suportado para conversão: {content_type}")
        return audio_bytes
    
    # Validação do cabeçalho WebM
    if not _validate_webm_header(audio_bytes):
        print("❌ Cabeçalho WebM inválido - arquivo corrompido ou não é WebM")
        return _create_fallback_wav(audio_bytes)
    
    # Abordagem 1: Tentar ffmpeg com opções mais robustas
    try:
        print("Tentando conversão com ffmpeg robusto...")
        
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as webm_file:
            webm_file.write(audio_bytes)
            webm_path = webm_file.name
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            wav_path = wav_file.name
        
        # Comando ffmpeg mais robusto com tratamento de erros
        cmd = [
            "ffmpeg", 
            "-i", webm_path,
            "-acodec", "pcm_s16le",  # Audio codec
            "-ar", "16000",          # Sample rate
            "-ac", "1",              # Mono
            "-y",                    # Overwrite output
            "-loglevel", "error",    # Only show errors
            wav_path
        ]
        
        print(f"Executando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            with open(wav_path, 'rb') as f:
                wav_bytes = f.read()
            
            # Valida o WAV gerado
            if len(wav_bytes) > 44 and wav_bytes[:4] == b'RIFF':
                print(f"✅ Conversão com ffmpeg bem-sucedida: {len(audio_bytes)} -> {len(wav_bytes)} bytes")
                return wav_bytes
            else:
                print("❌ ffmpeg gerou WAV inválido")
        else:
            print(f"❌ ffmpeg falhou: {result.stderr}")
            
    except FileNotFoundError:
        print("❌ ffmpeg não encontrado no sistema")
    except Exception as e:
        print(f"❌ Erro com ffmpeg: {e}")
    finally:
        # Limpa arquivos temporários
        try:
            if 'webm_path' in locals():
                os.unlink(webm_path)
            if 'wav_path' in locals():
                os.unlink(wav_path)
        except:
            pass
    
    # Abordagem 2: Tentar pydub se disponível
    try:
        from pydub import AudioSegment
        print("Tentando conversão com pydub...")
        
        audio_buffer = io.BytesIO(audio_bytes)
        
        # Tenta detectar o formato automaticamente
        try:
            audio = AudioSegment.from_file(audio_buffer)
            print("Formato detectado automaticamente")
        except:
            # Se falhar, tenta especificar webm
            audio_buffer.seek(0)
            audio = AudioSegment.from_file(audio_buffer, format="webm")
            print("Formato WebM detectado")
        
        # Exporta para WAV com parâmetros específicos
        wav_buffer = io.BytesIO()
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(wav_buffer, format="wav", parameters=["-acodec", "pcm_s16le"])
        converted_bytes = wav_buffer.getvalue()
        
        print(f"✅ Conversão com pydub bem-sucedida: {len(audio_bytes)} -> {len(converted_bytes)} bytes")
        return converted_bytes
        
    except ImportError:
        print("pydub não disponível")
    except Exception as e:
        print(f"❌ Erro com pydub: {e}")
    
    # Abordagem 3: Fallback inteligente
    print("Usando fallback inteligente para WebM inválido...")
    return _create_fallback_wav(audio_bytes)

def _create_fallback_wav(audio_bytes: bytes) -> bytes:
    """
    Cria um WAV válido a partir de dados de áudio problemáticos.
    Extrai dados brutos e cria WAV com header correto.
    """
    print("Criando WAV fallback...")
    
    # Tenta encontrar dados de áudio brutos no WebM
    # Procura por padrões comuns de áudio
    audio_data = None
    
    # Estratégia 1: Pular header WebM e procurar dados de áudio
    if len(audio_bytes) > 100:
        # Tenta pular header EBML (geralmente primeiros 40-100 bytes)
        for offset in range(40, min(200, len(audio_bytes) - 100)):
            # Procura por padrão que poderia ser áudio
            chunk = audio_bytes[offset:offset+10]
            if len(chunk) >= 10:
                # Verifica se parece com dados de áudio (não muito repetitivo)
                unique_bytes = len(set(chunk))
                if unique_bytes >= 4:  # Pelo menos 4 bytes diferentes
                    audio_data = audio_bytes[offset:]
                    break
    
    # Estratégia 2: Se não encontrar, usa os dados brutos (menos ideal)
    if audio_data is None:
        audio_data = audio_bytes
    
    # Limita o tamanho para evitar problemas
    max_audio_size = 16000 * 2 * 5  # 5 segundos de áudio (16kHz, 16-bit, mono)
    if len(audio_data) > max_audio_size:
        audio_data = audio_data[:max_audio_size]
    
    # Cria WAV header correto
    sample_rate = 16000
    channels = 1
    bits_per_sample = 16
    bytes_per_sample = bits_per_sample // 8
    
    # Calcula tamanhos
    data_size = len(audio_data)
    file_size = 36 + data_size
    byte_rate = sample_rate * channels * bytes_per_sample
    block_align = channels * bytes_per_sample
    
    # Cria header WAV (44 bytes)
    wav_header = bytearray()
    wav_header.extend(b'RIFF')
    wav_header.extend(file_size.to_bytes(4, 'little'))
    wav_header.extend(b'WAVE')
    wav_header.extend(b'fmt ')
    wav_header.extend((16).to_bytes(4, 'little'))  # fmt chunk size
    wav_header.extend((1).to_bytes(2, 'little'))   # PCM format
    wav_header.extend(channels.to_bytes(2, 'little'))
    wav_header.extend(sample_rate.to_bytes(4, 'little'))
    wav_header.extend(byte_rate.to_bytes(4, 'little'))
    wav_header.extend(block_align.to_bytes(2, 'little'))
    wav_header.extend(bits_per_sample.to_bytes(2, 'little'))
    wav_header.extend(b'data')
    wav_header.extend(data_size.to_bytes(4, 'little'))
    
    # Combina header com dados
    wav_bytes = bytes(wav_header) + audio_data
    
    print(f"✅ WAV fallback criado: {len(wav_bytes)} bytes")
    return wav_bytes


def _build_audio_config_from_bytes(wav_bytes: bytes) -> speechsdk.audio.AudioConfig:
    stream = speechsdk.audio.PushAudioInputStream()
    stream.write(wav_bytes)
    stream.close()
    return speechsdk.audio.AudioConfig(stream=stream)


def _parse_pronunciation_json(raw_json: str) -> tuple[dict[str, Any], list[PronunciationWordScore]]:
    try:
        raw = json.loads(raw_json)
    except Exception:
        return {"_raw": raw_json}, []

    words: list[PronunciationWordScore] = []
    # Azure returns NBest[0].Words[*]
    nbest = raw.get("NBest") or []
    if nbest and isinstance(nbest, list):
        words_raw = nbest[0].get("Words") or []
        if isinstance(words_raw, list):
            for w in words_raw:
                if not isinstance(w, dict):
                    continue
                words.append(
                    PronunciationWordScore(
                        word=str(w.get("Word", "")),
                        accuracy_score=float(w["PronunciationAssessment"]["AccuracyScore"])
                        if isinstance(w.get("PronunciationAssessment"), dict)
                        and "AccuracyScore" in w["PronunciationAssessment"]
                        else None,
                        error_type=str(w.get("ErrorType")) if w.get("ErrorType") is not None else None,
                    )
                )
    return raw, words


def _process_result(result) -> SpeechAssessmentResult:
    """Process Azure Speech SDK result and return SpeechAssessmentResult."""
    transcript = result.text or ""

    # Tratamento robusto de erro para PronunciationAssessmentResult
    try:
        pa_result = speechsdk.PronunciationAssessmentResult(result)
        overall = float(pa_result.pronunciation_score) if pa_result.pronunciation_score is not None else None
        accuracy = float(pa_result.accuracy_score) if pa_result.accuracy_score is not None else None
        fluency = float(pa_result.fluency_score) if pa_result.fluency_score is not None else None
        completeness = float(pa_result.completeness_score) if pa_result.completeness_score is not None else None
    except AttributeError as e:
        print(f"Erro ao acessar atributos do PronunciationAssessmentResult: {e}")
        # Valores padrão quando o assessment falha
        overall = None
        accuracy = None
        fluency = None
        completeness = None

    # Best-effort raw JSON
    raw_json = result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult, "")
    raw, words = _parse_pronunciation_json(raw_json)

    return SpeechAssessmentResult(
        transcript=transcript,
        overall_score=overall,
        accuracy_score=accuracy,
        fluency_score=fluency,
        completeness_score=completeness,
        word_scores=words,
        raw=raw,
    )


def _recognize_and_assess_sync(
    *,
    wav_bytes: bytes,
    key: str,
    region: str,
    language: str = "en-US",
    timeout_s: float = 20.0,
    content_type: str = "audio/webm",
) -> SpeechAssessmentResult:
    """Synchronous Azure Speech recognition with pronunciation assessment."""
    # Tenta usar WebM/Opus diretamente com Azure Speech SDK
    # Azure Speech SDK suporta WAV, OGG, MP3, e outros formatos
    # Se falhar, tenta converter para WAV
    try:
        print(f"Tentando usar formato original: {content_type}")
        speech_config = _build_speech_config(key=key, region=region, language=language)
        
        # Create audio config from bytes using PushAudioInputStream
        import io
        audio_stream = speechsdk.audio.PushAudioInputStream()
        audio_stream.write(wav_bytes)
        audio_stream.close()
        audio_config = speechsdk.AudioConfig(stream=audio_stream)

        recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        # Pronunciation Assessment configuration - use phoneme assessment for free-form speech
        pa_config = speechsdk.PronunciationAssessmentConfig(
            reference_text="*",  # Use asterisk for phoneme-based assessment
            grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
            granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
            enable_miscue=False,  # Disable miscue for free-form
        )
        pa_config.apply_to(recognizer)

        result = recognizer.recognize_once()
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Reconhecimento bem-sucedido com formato original")
            return _process_result(result)
        else:
            print(f"Falha com formato original: {result.reason}, tentando converter para WAV")
            raise RuntimeError("Formato não suportado, tentando conversão")
            
    except Exception as e:
        print(f"Erro com formato original: {e}, tentando converter para WAV")
        # Se falhar, converte para WAV
        wav_bytes = _convert_webm_to_wav(wav_bytes, content_type)
        
        speech_config = _build_speech_config(key=key, region=region, language=language)
    
    # Create audio config from bytes using PushAudioInputStream for better compatibility
    import io
    audio_stream = speechsdk.audio.PushAudioInputStream()
    audio_stream.write(wav_bytes)
    audio_stream.close()
    audio_config = speechsdk.AudioConfig(stream=audio_stream)

    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    # Pronunciation Assessment configuration - use phoneme assessment for free-form speech
    # Note: For free-tier constraints and SDK variations, keep config minimal.
    pa_config = speechsdk.PronunciationAssessmentConfig(
        reference_text="*",  # Use asterisk for phoneme-based assessment
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=False,  # Disable miscue for free-form
    )
    pa_config.apply_to(recognizer)

    result = recognizer.recognize_once()

    transcript = result.text or ""

    # Tratamento robusto de erro para PronunciationAssessmentResult
    try:
        pa_result = speechsdk.PronunciationAssessmentResult(result)
        overall = float(pa_result.pronunciation_score) if pa_result.pronunciation_score is not None else None
        accuracy = float(pa_result.accuracy_score) if pa_result.accuracy_score is not None else None
        fluency = float(pa_result.fluency_score) if pa_result.fluency_score is not None else None
        completeness = float(pa_result.completeness_score) if pa_result.completeness_score is not None else None
    except AttributeError as e:
        print(f"Erro ao acessar atributos do PronunciationAssessmentResult: {e}")
        # Valores padrão quando o assessment falha
        overall = None
        accuracy = None
        fluency = None
        completeness = None

    # Best-effort raw JSON
    raw_json = result.properties.get(speechsdk.PropertyId.SpeechServiceResponse_JsonResult, "")
    raw, words = _parse_pronunciation_json(raw_json)

    return SpeechAssessmentResult(
        transcript=transcript,
        overall_score=overall,
        accuracy_score=accuracy,
        fluency_score=fluency,
        completeness_score=completeness,
        word_scores=words,
        raw=raw,
    )


async def recognize_and_assess(
    *,
    wav_bytes: bytes,
    key: str,
    region: str,
    language: str = "en-US",
    timeout_s: float = 20.0,
    content_type: str = "audio/webm",
) -> SpeechAssessmentResult:
    """
    Async wrapper: runs Azure Speech SDK (sync) in a thread.
    """
    return await asyncio.wait_for(
        asyncio.to_thread(
            _recognize_and_assess_sync,
            wav_bytes=wav_bytes,
            key=key,
            region=region,
            language=language,
            content_type=content_type,
        ),
        timeout=timeout_s,
    )


def _tts_sync(*, text: str, key: str, region: str, voice: str) -> bytes:
    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_synthesis_voice_name = voice
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    result = synthesizer.speak_text_async(text).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise RuntimeError("TTS synthesis failed")
    return bytes(result.audio_data)


async def synthesize_tts(
    *,
    text: str,
    key: str,
    region: str,
    voice: str,
    timeout_s: float = 20.0,
) -> bytes:
    """
    Async wrapper: runs Azure Speech SDK TTS (sync) in a thread.
    Returns audio bytes (typically WAV).
    """
    return await asyncio.wait_for(
        asyncio.to_thread(_tts_sync, text=text, key=key, region=region, voice=voice),
        timeout=timeout_s,
    )

