'use strict';

angular.module('caracolApp', [
  'ngRoute',
  'ui.bootstrap',
  'caracolApp.controllers',
  'caracolApp.services'
])
.config(function ($routeProvider) {
  $routeProvider
    .when('/', {
      templateUrl: '/views/main.html',
      controller: 'MainCtrl'
    })
    .when('/clippings', {
     templateUrl: '/views/clippings.html',
     controller: 'ClippingsCtrl'
    })
    .otherwise({
      redirectTo: '/'
    });
});