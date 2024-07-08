using 'main.bicep'

param openAiDeployments = [
  {
    name: 'gpt-4o'
    version: '2024-05-13'
    capacity: 30
  }
]

param tags = {
  environment: 'iot-hub-messaging'
}
