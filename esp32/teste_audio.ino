#include <WiFi.h>
#include <HTTPClient.h>
#include <SPIFFS.h>

// Credenciais WiFi
const char* ssid = "VIVOFIBRA-FC61";
const char* password = "gBTZEis3kZ";

// URL do Webhook
const char* webhookURL = "https://hook.us2.make.com/hi5ekcs0a9m517a44xpykc0vns3e19l3";

// Configuração do pino e parâmetros
const int pinoEntrada = 35; // Pino de entrada analógica
const int taxaAmostragem = 8000; // Taxa de amostragem (8kHz)
const int duracao = 1000; // Duração da captura em milissegundos

void setup() {
  Serial.begin(115200);

  // Inicializa SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("Erro ao inicializar SPIFFS");
    return;
  }

  // Conecta ao WiFi
  Serial.println("Conectando ao WiFi...");
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Conectando...");
  }
  Serial.println("WiFi conectado!");

  // Envio de teste inicial
  enviarTeste();
}

void loop() {
  // Nome do arquivo temporário
  const char* arquivoAudio = "/audio.txt";

  // Captura as amostras e salva no arquivo
  if (capturarAmostras(arquivoAudio)) {
    // Envia o arquivo para o webhook
    enviarArquivo(arquivoAudio);
  }

  delay(5000); // Espera antes da próxima captura
}

// Função para capturar amostras de áudio e salvar no arquivo
bool capturarAmostras(const char* caminho) {
  File arquivo = SPIFFS.open(caminho, FILE_WRITE);
  if (!arquivo) {
    Serial.println("Erro ao abrir o arquivo para escrita");
    return false;
  }

  unsigned long startMillis = millis();
  while (millis() - startMillis < duracao) {
    int amostra = analogRead(pinoEntrada); // Lê o sinal analógico
    int valorMapeado = map(amostra, 0, 4095, 0, 255); // Mapeia para 8 bits
    arquivo.println(valorMapeado); // Salva no arquivo
    delayMicroseconds(1000000 / taxaAmostragem); // Controla a taxa de amostragem
  }

  arquivo.close();
  Serial.println("Amostras salvas no arquivo!");
  return true;
}

// Função para enviar o arquivo para o webhook
void enviarArquivo(const char* caminho) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Inicializa o cliente HTTP
    http.begin(webhookURL);
    http.addHeader("Content-Type", "application/json"); // Define o tipo de conteúdo

    // Abre o arquivo para leitura
    File arquivo = SPIFFS.open(caminho, FILE_READ);
    if (!arquivo) {
      Serial.println("Erro ao abrir o arquivo para leitura");
      return;
    }

    // Lê o conteúdo do arquivo
    String conteudo = "";
    while (arquivo.available()) {
      char c = arquivo.read();
      if (c == '\n') continue; // Remove quebras de linha
      conteudo += c;
    }

    // Cria o JSON com os parâmetros esperados
    String jsonPayload = "{";
    jsonPayload += "\"file\": {";
    jsonPayload += "\"name\": \"audio.txt\",";
    jsonPayload += "\"data\": \"" + conteudo + "\"";
    jsonPayload += "}}";

    // Envia a requisição POST
    Serial.println("Enviando JSON:");
    Serial.println(jsonPayload);

    int httpResponseCode = http.POST(jsonPayload);

    // Verifica a resposta
    if (httpResponseCode > 0) {
      Serial.println("Arquivo enviado com sucesso!");
      Serial.println("Código de resposta: " + String(httpResponseCode));
      Serial.println("Resposta: " + http.getString());
    } else {
      Serial.println("Erro ao enviar: " + String(httpResponseCode));
    }

    arquivo.close();
    http.end(); // Finaliza a conexão
  } else {
    Serial.println("WiFi desconectado, não foi possível enviar.");
  }
}

// Função para enviar um teste inicial
void enviarTeste() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(webhookURL);
    http.addHeader("Content-Type", "application/json");

    String jsonPayload = "{";
    jsonPayload += "\"file\": {";
    jsonPayload += "\"name\": \"test.txt\",";
    jsonPayload += "\"data\": \"TESTE_INICIAL\"";
    jsonPayload += "}}";

    Serial.println("Enviando teste inicial:");
    Serial.println(jsonPayload);

    int httpResponseCode = http.POST(jsonPayload);
    if (httpResponseCode > 0) {
      Serial.println("Teste enviado com sucesso!");
      Serial.println("Resposta: " + http.getString());
    } else {
      Serial.println("Erro ao enviar teste: " + String(httpResponseCode));
    }

    http.end();
  }
}