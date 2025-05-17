@description('Name of the App Service app')
param appName string = 'my-sre-app-${uniqueString(resourceGroup().id)}'

@description('Name of the App Service Plan')
param appServicePlanName string = '${appName}-plan'

@description('Location for the resources')
param location string = resourceGroup().location

@description('Name of the deployment slot')
param slotName string = 'broken'


@description('Name of the Application Insights resource')
param appInsightsName string = '${appName}-ai'

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

resource appInsightsKey 'Microsoft.Web/sites/config@2022-09-01' = {
  name: '${appName}/appsettings'
  properties: {
    'APPINSIGHTS_INSTRUMENTATIONKEY': appInsights.properties.InstrumentationKey
    'APPLICATIONINSIGHTS_CONNECTION_STRING': appInsights.properties.ConnectionString
    'ApplicationInsightsAgent_EXTENSION_VERSION': '~3'
  }
  dependsOn: [ webApp, appInsights ]
}


resource appServicePlan 'Microsoft.Web/serverfarms@2022-09-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'S1'
    tier: 'Standard'
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
      linuxFxVersion: 'PYTHON|3.13'
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
      linuxFxVersion: 'PYTHON|3.13'
      appCommandLine: '/home/site/wwwroot/startup.sh'
    }
  }
}

resource logSettings 'Microsoft.Web/sites/config@2022-09-01' = {
  name: '${appName}'
  dependsOn: [
    webApp
  ]
  properties: {
    logs: {
      applicationLogs: {
        fileSystem: {
          level: 'Information'
        }
      }
      httpLogs: {
        fileSystem: {
          retentionInMb: 35
          retentionInDays: 3
          enabled: true
        }
      }
      detailedErrorMessages: {
        enabled: true
      }
      failedRequestsTracing: {
        enabled: true
      }
    }
  }
}


output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output appInsightsConnectionString string = appInsights.properties.ConnectionString
