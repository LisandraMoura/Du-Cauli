#include "driver/i2s.h"
#include <WiFi.h>
#include <HTTPClient.h>

// Configurações do I2S para o INMP441
#define I2S_WS 4     // Pino WS (Word Select)
#define I2S_SD 15    // Pino SD (Serial Data)
#define I2S_SCK 14   // Pino SCK (Serial Clock)
#define I2S_PORT I2S_NUM_0

// Configurações do botão e LED
#define BUTTON_PIN 22  // Pino onde o botão está conectado
#define LED_PIN 23     // Pino onde o LED está conectado

// Configurações do áudio
#define SAMPLE_RATE 16000  // Taxa de amostragem (16 kHz)
#define BUFFER_SIZE 512    // Tamanho do buffer para leitura
#define CHUNK_DURATION 30  // Duração do chunk em segundos
#define CHUNK_SIZE (SAMPLE_RATE * 2 * CHUNK_DURATION) // Tamanho do chunk (16 bits = 2 bytes por amostra)

// Configurações do Wi-Fi
const char* ssid = "CLARO_2G74EAB6";
const char* password = "EF74EAB6";
const char* serverName = "https://hook.us2.make.com/SEU_WEBHOOK_URL_AQUI";

// Estados do sistema
bool isRecording = false; // Indica se está gravando ou não
bool lastButtonState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 100; // Tempo para eliminar "rebotes"

// Buffers
uint8_t audioChunk[CHUNK_SIZE];          // Buffer para armazenar o chunk de áudio
uint8_t wavBuffer[CHUNK_SIZE + 44];     // Buffer com espaço para o cabeçalho WAV
size_t chunkIndex = 0;                  // Índice do buffer atual

// Função para adicionar cabeçalho WAV
void addWavHeader(uint8_t* buffer, size_t dataSize) {
    const uint32_t fileSize = 36 + dataSize;
    const uint16_t audioFormat = 1;
    const uint16_t numChannels = 1;
    const uint32_t byteRate = SAMPLE_RATE * numChannels * 2;
    const uint16_t blockAlign = numChannels * 2;
    const uint16_t bitsPerSample = 16;

    memcpy(buffer, "RIFF", 4);
    memcpy(buffer + 4, &fileSize, 4);
    memcpy(buffer + 8, "WAVEfmt ", 8);
    uint32_t subChunk1Size = 16;
    memcpy(buffer + 16, &subChunk1Size, 4);
    memcpy(buffer + 20, &audioFormat, 2);
    memcpy(buffer + 22, &numChannels, 2);
    memcpy(buffer + 24, &SAMPLE_RATE, 4);
    memcpy(buffer + 28, &byteRate, 4);
    memcpy(buffer + 32, &blockAlign, 2);
    memcpy(buffer + 34, &bitsPerSample, 2);
    memcpy(buffer + 36, "data", 4);
    memcpy(buffer + 40, &dataSize, 4);
}

// Inicialização do I2S
void i2s_init() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_I2S,
        .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
        .dma_buf_count = 4,
        .dma_buf_len = BUFFER_SIZE,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0};

    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_SCK,
        .ws_io_num = I2S_WS,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_SD};

    i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_PORT, &pin_config);
}

void setup() {
    Serial.begin(115200); // Inicializar comunicação serial

    // Inicializar I2S
    i2s_init();
    Serial.println("I2S inicializado.");

    // Configurar botão e LED
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW); // LED desligado inicialmente

    // Conectar ao Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Conectando ao WiFi...");
    }
    Serial.println("Conectado ao WiFi.");
}

void loop() {
    // Ler estado atual do botão
    bool buttonState = digitalRead(BUTTON_PIN);

    // Detectar mudança de estado no botão com debounce
    if (buttonState == LOW && lastButtonState == HIGH && (millis() - lastDebounceTime) > debounceDelay) {
        lastDebounceTime = millis();
        isRecording = !isRecording; // Alternar estado de gravação

        if (isRecording) {
            digitalWrite(LED_PIN, HIGH); // Acender LED
            Serial.println("Gravação iniciada.");
            chunkIndex = 0; // Reinicia o índice do chunk
        } else {
            digitalWrite(LED_PIN, LOW); // Apagar LED
            Serial.println("Gravação parada.");
        }
    }

    lastButtonState = buttonState;

    // Gravação e envio de chunks de áudio
    if (isRecording) {
        uint8_t buffer[BUFFER_SIZE]; // Buffer temporário para leitura do I2S
        size_t bytesRead;

        // Ler dados do microfone
        i2s_read(I2S_PORT, buffer, BUFFER_SIZE, &bytesRead, portMAX_DELAY);

        // Copiar dados para o chunk
        for (size_t i = 0; i < bytesRead && chunkIndex < CHUNK_SIZE; i++) {
            audioChunk[chunkIndex++] = buffer[i];
        }

        // Enviar o chunk quando estiver completo
        if (chunkIndex >= CHUNK_SIZE) {
            addWavHeader(wavBuffer, CHUNK_SIZE);
            memcpy(wavBuffer + 44, audioChunk, CHUNK_SIZE); // Copiar dados após o cabeçalho
            sendAudioChunk(wavBuffer, CHUNK_SIZE + 44);
            chunkIndex = 0; // Reinicia o índice do chunk
        }
    }
}

// Enviar um chunk de áudio para o Make
void sendAudioChunk(uint8_t* buffer, size_t size) {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(serverName);

        // Configura o cabeçalho para dados binários
        http.addHeader("Content-Type", "application/octet-stream");

        // Envia os dados binários
        int httpResponseCode = http.POST(buffer, size);

        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.println("Chunk enviado com sucesso.");
            Serial.println(response);
        } else {
            Serial.println("Erro ao enviar o chunk.");
        }

        http.end();
    } else {
        Serial.println("WiFi desconectado.");
    }
}