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


def _convert_webm_to_wav(audio_bytes: bytes, content_type: str = "audio/webm") -> bytes:
    """
    Converte WebM/Opus para WAV PCM usando múltiplas abordagens.
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
    
    # Abordagem 1: Tentar usar pydub se disponível
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
        
        # Exporta para WAV
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        converted_bytes = wav_buffer.getvalue()
        
        print(f"Conversão com pydub bem-sucedida: {len(audio_bytes)} -> {len(converted_bytes)} bytes")
        return converted_bytes
        
    except ImportError:
        print("pydub não disponível, tentando outras abordagens...")
    except Exception as e:
        print(f"Erro com pydub: {e}")
    
    # Abordagem 2: Tentar ffmpeg via subprocess
    try:
        print("Tentando conversão com ffmpeg...")
        
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as webm_file:
            webm_file.write(audio_bytes)
            webm_path = webm_file.name
        
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as wav_file:
            wav_path = wav_file.name
        
        # Comando ffmpeg simplificado
        cmd = ["ffmpeg", "-i", webm_path, "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", wav_path, "-y"]
        
        print(f"Executando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            with open(wav_path, 'rb') as f:
                wav_bytes = f.read()
            
            print(f"Conversão com ffmpeg bem-sucedida: {len(audio_bytes)} -> {len(wav_bytes)} bytes")
            return wav_bytes
        else:
            print(f"ffmpeg falhou: {result.stderr}")
            
    except FileNotFoundError:
        print("ffmpeg não encontrado no sistema")
    except Exception as e:
        print(f"Erro com ffmpeg: {e}")
    finally:
        # Limpa arquivos temporários
        try:
            if 'webm_path' in locals():
                os.unlink(webm_path)
            if 'wav_path' in locals():
                os.unlink(wav_path)
        except:
            pass
    
    # Abordagem 3: Tentar criar WAV manualmente (limitado mas melhor que nada)
    try:
        print("Tentando criar WAV manualmente como último recurso...")
        
        # Cria um cabeçalho WAV simples (16kHz, mono, 16-bit)
        sample_rate = 16000
        channels = 1
        bits_per_sample = 16
        
        # Se os bytes do WebM forem muito pequenos, não adianta tentar
        if len(audio_bytes) < 1000:
            print("Arquivo de áudio muito pequeno, não é possível converter")
            return audio_bytes
        
        # Tenta extrair dados brutos (muito limitado, mas pode funcionar em alguns casos)
        # NOTA: Esta é uma abordagem muito básica e pode não funcionar para WebM real
        wav_header = io.BytesIO()
        
        # WAV header (44 bytes)
        wav_header.write(b'RIFF')
        wav_header.write((len(audio_bytes) + 36).to_bytes(4, 'little'))
        wav_header.write(b'WAVE')
        wav_header.write(b'fmt ')
        wav_header.write((16).to_bytes(4, 'little'))  # fmt chunk size
        wav_header.write((1).to_bytes(2, 'little'))   # PCM
        wav_header.write(channels.to_bytes(2, 'little'))
        wav_header.write(sample_rate.to_bytes(4, 'little'))
        wav_header.write((sample_rate * channels * bits_per_sample // 8).to_bytes(4, 'little'))
        wav_header.write((channels * bits_per_sample // 8).to_bytes(2, 'little'))
        wav_header.write(bits_per_sample.to_bytes(2, 'little'))
        wav_header.write(b'data')
        wav_header.write(len(audio_bytes).to_bytes(4, 'little'))
        
        # Combina header com dados (não ideal, mas como fallback)
        wav_bytes = wav_header.getvalue() + audio_bytes
        
        print(f"WAV manual criado: {len(wav_bytes)} bytes")
        return wav_bytes
        
    except Exception as e:
        print(f"Erro na criação manual de WAV: {e}")
    
    # Abordagem 4: Retornar erro informativo
    print("Não foi possível converter WebM para WAV com as ferramentas disponíveis")
    print("Sugestão: Instale ffmpeg no sistema ou configure o frontend para enviar WAV")
    
    # Retorna bytes originais para que o erro seja capturado pelo Azure SDK
    # Isso dará uma mensagem de erro mais clara sobre o formato não suportado
    return audio_bytes


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

        # Pronunciation Assessment configuration
        pa_config = speechsdk.PronunciationAssessmentConfig(
            reference_text="",
            grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
            granularity=speechsdk.PronunciationAssessmentGranularity.Word,
            enable_miscue=True,
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

    # Pronunciation Assessment configuration
    # Note: For free-tier constraints and SDK variations, keep config minimal.
    pa_config = speechsdk.PronunciationAssessmentConfig(
        reference_text="",  # free-form assessment
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Word,
        enable_miscue=True,
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

