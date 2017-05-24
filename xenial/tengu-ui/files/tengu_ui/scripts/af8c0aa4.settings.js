
/*!
Copyright (c) 2002-2016 "Neo Technology,"
Network Engine for Objects in Lund AB [http://neotechnology.com]

This file is part of Neo4j.

Neo4j is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
var baseURL, restAPI;

baseURL = '';

restAPI = baseURL + "/db/data";

angular.module('neo4jApp.settings', ['neo4jApp.utils']).constant('Settings', {
  cmdchar: ':',
  endpoint: {
    console: baseURL + "/db/manage/server/console",
    version: baseURL + "/db/manage/server/version",
    jmx: baseURL + "/db/manage/server/jmx/query",
    rest: restAPI,
    cypher: restAPI + "/cypher",
    transaction: restAPI + "/transaction",
    authUser: baseURL + "/user",
    tengu: "https://demobackend.tengu.io",
    bundles: "https://raw.githubusercontent.com/tengu-team/bundle-{{bundlename}}/master/bundle.json",
    mappings: "https://raw.githubusercontent.com/IBCNServices/tengu-charms/master/bundles/{{bundlename}}/mapping.json"
  },
  needAuthZ: true,
  useSojobo: true,
  apiKey: "f3f5367b3c28aadbc7b0423885f05624c228e4d8fdf8fbe042b872c4ea0da984",
  featureflags: 'FEATURE_FLAG_AUTH',
  host: baseURL,
  maxExecutionTime: 3600,
  heartbeat: 60,
  maxFrames: 50,
  maxHistory: 100,
  maxNeighbours: 100,
  initialNodeDisplay: 300,
  maxRows: 1000,
  filemode: false,
  maxRawSize: 5000,
  scrollToTop: true,
  showVizDiagnostics: false,
  acceptsReplies: false,
  enableMotd: true,
  initCmd: ":play tengu",
  refreshInterval: 10,
  userName: "Tengu Friend",
  theme: "normal",
  retainConnectionCredentials: true,
  shouldReportUdc: false,
  experimentalFeatures: false,
  useBolt: false,
  boltHost: "",
  shownTermsAndPrivacy: false,
  acceptedTermsAndPrivacy: false,
  onboarding: false,
  showSampleScripts: true
});

angular.module('neo4jApp.settings').service('SettingsStore', [
  '$rootScope', 'localStorageService', 'Settings', 'Utils', function($rootScope, localStorageService, Settings, Utils) {
    var originalSettings;
    originalSettings = angular.copy(Settings);
    return {
      load: function() {
        var settings;
        settings = localStorageService.get('settings');
        if (angular.isObject(settings)) {
          return Utils.extendDeep(Settings, settings);
        }
      },
      reset: function() {
        localStorageService.remove('settings');
        return angular.extend(Settings, originalSettings);
      },
      save: function() {
        localStorageService.set('settings', angular.copy(Settings));
        return $rootScope.$broadcast('settings:saved');
      }
    };
  }
]);

angular.module('neo4jApp.settings').run([
  'SettingsStore', function(SettingsStore) {
    return SettingsStore.load();
  }
]);
