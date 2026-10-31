/**
 * Audio Recording and Speech Recognition Utilities for Raahi.
 * Provides resilient, multi-tiered voice interaction:
 * 1. Native Web Speech Recognition (Google Chrome / Edge) for instantaneous real-time transcription.
 * 2. Pure JavaScript 16kHz mono PCM WAV Audio Recorder for Sarvam AI Saaras STT fallback.
 */

export interface SpeechRecognitionCallbacks {
  onInterim: (text: string) => void;
  onFinal: (text: string) => void;
  onError: (error: string) => void;
  onEnd: () => void;
}

export function isWebSpeechSupported(): boolean {
  if (typeof window === 'undefined') return false;
  return Boolean((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition);
}

/**
 * Starts real-time browser-native speech recognition.
 */
export function startLiveSpeechRecognition(
  language: 'hi' | 'en',
  callbacks: SpeechRecognitionCallbacks
): { stop: () => void } {
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  if (!SpeechRecognition) {
    callbacks.onError('not-supported');
    return { stop: () => { } };
  }

  const recognition = new SpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;
  recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';

  let finalTranscript = '';

  recognition.onresult = (event: any) => {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; ++i) {
      const trans = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += trans;
      } else {
        interim += trans;
      }
    }
    if (finalTranscript) {
      callbacks.onFinal(finalTranscript);
    } else if (interim) {
      callbacks.onInterim(interim);
    }
  };

  recognition.onerror = (event: any) => {
    callbacks.onError(event.error || 'speech-error');
  };

  recognition.onend = () => {
    callbacks.onEnd();
  };

  try {
    recognition.start();
  } catch (err: any) {
    callbacks.onError(err?.message || 'start-failed');
  }

  return {
    stop: () => {
      try {
        recognition.stop();
      } catch {
        // ignore
      }
    }
  };
}

/**
 * Converts PCM Float32Array to 16kHz mono standard WAV Blob.
 */
export function exportWavBlob(samples: Float32Array, sampleRate: number): Blob {
  const targetSampleRate = 16000;
  const downsampled = downsampleBuffer(samples, sampleRate, targetSampleRate);

  const buffer = new ArrayBuffer(44 + downsampled.length * 2);
  const view = new DataView(buffer);

  const writeString = (offset: number, string: string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  };

  // RIFF Chunk
  writeString(0, 'RIFF');
  view.setUint32(4, 36 + downsampled.length * 2, true);
  writeString(8, 'WAVE');

  // fmt Sub-chunk
  writeString(12, 'fmt ');
  view.setUint32(16, 16, true); // SubChunk1Size (16 for PCM)
  view.setUint16(20, 1, true); // AudioFormat (1 for PCM)
  view.setUint16(22, 1, true); // NumChannels (1 mono)
  view.setUint32(24, targetSampleRate, true); // SampleRate (16000)
  view.setUint32(28, targetSampleRate * 2, true); // ByteRate (SampleRate * 1 * 16/8)
  view.setUint16(32, 2, true); // BlockAlign (1 * 16/8)
  view.setUint16(34, 16, true); // BitsPerSample (16 bits)

  // data Sub-chunk
  writeString(36, 'data');
  view.setUint32(40, downsampled.length * 2, true);

  // Write 16-bit PCM samples
  let offset = 44;
  for (let i = 0; i < downsampled.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, downsampled[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
  }

  return new Blob([view], { type: 'audio/wav' });
}

function downsampleBuffer(buffer: Float32Array, sampleRate: number, outSampleRate: number): Float32Array {
  if (outSampleRate >= sampleRate) {
    return buffer;
  }
  const ratio = sampleRate / outSampleRate;
  const newLength = Math.round(buffer.length / ratio);
  const result = new Float32Array(newLength);
  let offsetResult = 0;
  let offsetBuffer = 0;

  while (offsetResult < result.length) {
    const nextOffsetBuffer = Math.round((offsetResult + 1) * ratio);
    let accum = 0;
    let count = 0;
    for (let i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
      accum += buffer[i];
      count++;
    }
    result[offsetResult] = count > 0 ? accum / count : 0;
    offsetResult++;
    offsetBuffer = nextOffsetBuffer;
  }
  return result;
}

export interface WavRecorder {
  stop: () => Promise<Blob>;
  cancel: () => void;
}

/**
 * Starts 16kHz PCM audio recording using the Web Audio API.
 */
export async function startWavRecording(): Promise<WavRecorder> {
  const stream = await navigator.mediaDevices.getUserMedia({
    audio: {
      channelCount: 1,
      echoCancellation: true,
      noiseSuppression: true
    }
  });

  const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
  const audioContext = new AudioCtx();
  const source = audioContext.createMediaStreamSource(stream);
  const processor = audioContext.createScriptProcessor(4096, 1, 1);
  const chunks: Float32Array[] = [];

  processor.onaudioprocess = (e) => {
    const channelData = e.inputBuffer.getChannelData(0);
    chunks.push(new Float32Array(channelData));
  };

  source.connect(processor);
  processor.connect(audioContext.destination);

  return {
    stop: async () => {
      source.disconnect();
      processor.disconnect();
      stream.getTracks().forEach(track => track.stop());
      const sRate = audioContext.sampleRate;
      await audioContext.close();

      let totalLen = 0;
      for (const c of chunks) totalLen += c.length;
      const merged = new Float32Array(totalLen);
      let offset = 0;
      for (const c of chunks) {
        merged.set(c, offset);
        offset += c.length;
      }
      return exportWavBlob(merged, sRate);
    },
    cancel: () => {
      try {
        source.disconnect();
        processor.disconnect();
        stream.getTracks().forEach(track => track.stop());
        audioContext.close();
      } catch {
        // ignore
      }
    }
  };
}

