@description('Name of the App Service app')
param appName string = 'my-sre-app-${uniqueString(resourceGroup().id)}'

@description('Name of the App Service Plan')
param appServicePlanName string = '${appName}-plan'

@description('Location for the resources')
param location string = resourceGroup().location

@description('Name of the deployment slot')
param slotName string = 'broken'


resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'P0v3'
    tier: 'PremiumV3'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2022-09-01' = {
  name: appName
  location: location
  tags: {
    'azd-service-name': 'web'
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      alwaysOn: true
      linuxFxVersion: 'PYTHON|3.13'
      appCommandLine: '/home/site/wwwroot/startup.sh'      
    }
  }
}

resource deploymentSlot 'Microsoft.Web/sites/slots@2022-09-01' = {
  name: '${appName}/${slotName}'
  dependsOn: [
    webApp
  ]
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      alwaysOn: true
      linuxFxVersion: 'PYTHON|3.13'
      appCommandLine: '/home/site/wwwroot/startup.sh'  
      appSettings: [
        {
          name: 'MEMORY_BUG'
          value: '1'
        }
      ]
    }
  }
}

resource logSettings 'Microsoft.Web/sites/config@2022-09-01' = {
  name: '${appName}/web'
  dependsOn: [
    webApp
  ]
  properties: {
    applicationLogging: {
      fileSystem: {
        level: 'Information'
        retentionInDays: 3
      }
    }
  }
}

output AZURE_WEB_APP_NAME string = webApp.name
