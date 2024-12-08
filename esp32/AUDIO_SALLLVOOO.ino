#include "FS.h"       // Biblioteca do sistema de arquivos
#include "SD_MMC.h"   // Biblioteca para controle do SD no modo SDMMC

// Configurações do cartão SDMMC
#define SD_MMC_CMD 15  // Linha CMD do cartão SD
#define SD_MMC_CLK 14  // Linha de clock do cartão SD
#define SD_MMC_D0  2   // Linha de dados D0 do cartão SD

// Configuração do microfone MAX9814
#define MIC_PIN 34        // Entrada analógica do microfone MAX9814 (ADC1)
#define SAMPLE_RATE 16000 // Taxa de amostragem (16 kHz)
#define NUM_CHANNELS 1    // Número de canais (Mono)
#define BITS_PER_SAMPLE 16 // Bits por amostra (16 bits)

// Variáveis globais
File wavFile; // Arquivo WAV

void writeWavHeader(fs::File &file, uint32_t dataSize) {
    // "RIFF" Header
    const char riff[] = "RIFF";
    file.write((const uint8_t*)riff, 4); // Chunk ID

    // Tamanho do arquivo
    uint32_t fileSize = 36 + dataSize;
    file.write((const uint8_t*)&fileSize, 4); // File size

    // "WAVE" Format
    const char wave[] = "WAVE";
    file.write((const uint8_t*)wave, 4); // Format

    // "fmt " Subchunk1 ID
    const char fmt[] = "fmt ";
    file.write((const uint8_t*)fmt, 4); // Subchunk1 ID

    // Subchunk1 Size (16 for PCM)
    uint32_t subchunk1Size = 16;
    file.write((const uint8_t*)&subchunk1Size, 4); // Subchunk1 Size

    // Audio Format (1 for PCM)
    uint16_t audioFormat = 1;
    file.write((const uint8_t*)&audioFormat, 2); // Audio Format

    // Número de canais (Mono)
    uint16_t numChannels = NUM_CHANNELS;
    file.write((const uint8_t*)&numChannels, 2); // Number of channels

    // Taxa de amostragem (16 kHz)
    uint32_t sampleRate = SAMPLE_RATE;
    file.write((const uint8_t*)&sampleRate, 4); // Sample rate

    // Byte rate (SampleRate * NumChannels * BitsPerSample/8)
    uint32_t byteRate = SAMPLE_RATE * NUM_CHANNELS * (BITS_PER_SAMPLE / 8);
    file.write((const uint8_t*)&byteRate, 4); // Byte rate

    // Bloco de alinhamento (NumChannels * BitsPerSample/8)
    uint16_t blockAlign = NUM_CHANNELS * (BITS_PER_SAMPLE / 8);
    file.write((const uint8_t*)&blockAlign, 2); // Block align

    // Bits por amostra (16 bits)
    uint16_t bitsPerSample = BITS_PER_SAMPLE;
    file.write((const uint8_t*)&bitsPerSample, 2); // Bits per sample

    // "data" Subchunk2 ID
    const char data[] = "data";
    file.write((const uint8_t*)data, 4); // Subchunk2 ID

    // Tamanho dos dados de áudio
    file.write((const uint8_t*)&dataSize, 4); // Subchunk2 size
}

// Função para iniciar a gravação
void startRecording() {
    // Cria o arquivo WAV
    wavFile = SD_MMC.open("/audio.wav", FILE_WRITE);
    if (!wavFile) {
        Serial.println("Falha ao criar o arquivo WAV!");
        return;
    }

    // Escreve o cabeçalho WAV com um tamanho de dados inicial de 0
    writeWavHeader(wavFile, 0);
    Serial.println("Gravação iniciada...");
}

// Função para finalizar a gravação
void stopRecording(uint32_t dataSize) {
    // Reescreve o cabeçalho com o tamanho de dados correto
    wavFile.seek(0);
    writeWavHeader(wavFile, dataSize);
    wavFile.close();
    Serial.println("Gravação finalizada.");
}

void setup() {
    Serial.begin(115200);

    // Configura os pinos do SDMMC
    SD_MMC.setPins(SD_MMC_CLK, SD_MMC_CMD, SD_MMC_D0);

    // Inicializa o cartão SD
    if (!SD_MMC.begin("/sdcard", true, true, SDMMC_FREQ_DEFAULT, 5)) {
        Serial.println("Falha ao montar o cartão SD!");
        return;
    }

    pinMode(MIC_PIN, INPUT); // Configura o pino do microfone
    startRecording();        // Inicia a gravação
}

void loop() {
    static uint32_t dataSize = 0;         // Tamanho dos dados gravados
    static uint32_t startMillis = millis();
    static uint32_t lastSampleTime = micros(); // Última vez que uma amostra foi capturada

    // Calcula o intervalo entre amostras (em microssegundos)
    const uint32_t sampleInterval = 1000000 / SAMPLE_RATE; // 1 segundo em µs dividido pela taxa de amostragem

    // Verifica se é hora de capturar a próxima amostra
    if (micros() - lastSampleTime >= sampleInterval) {
        lastSampleTime += sampleInterval; // Atualiza o tempo da próxima amostra

        // Leitura do microfone
        int micValue = analogRead(MIC_PIN);

        // Converte para 16 bits e grava no arquivo
        int16_t sample = (int16_t)((micValue - 2048) * 16); // Ajusta para 16 bits
        wavFile.write((uint8_t *)&sample, sizeof(sample));
        dataSize += sizeof(sample);
    }

    // Para gravação após 10 segundos
    if (millis() - startMillis > 20000) {
        stopRecording(dataSize);
        while (1); // Para o loop
    }
}
