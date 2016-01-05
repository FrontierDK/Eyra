// **************************************************************************************** //

//                                         TODO                                             //

// sanitize user input for speakerId, etc.
// add try catch, for example with JSON.stringify
// CONSIDER moving logic in recordingsCallback() and send() to a service or something, 
//   and out of main controller 
// Think about if we want to have a limit on how many sessions are sent in "sync"

// ***************************************************************************************** //

'use strict';

var putOnline = false;
var BACKENDURL = putOnline ? 'bakendi.localtunnel.me' : '127.0.0.1:5000';

angular.module('daApp', ['LocalForageModule'])

.constant('invalidTitle', 'no_data.wav') // sentinel value for invalid recordings

// make sure Angular doesn't prepend "unsafe:" to the blob: url
.config( [
      '$compileProvider',
      function( $compileProvider )
      {   
          $compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|ftp|mailto|blob):/);
      }
])

// fix some angular issue with <audio ng-src="{{var}}"></audio>
// http://stackoverflow.com/questions/20049261/sce-trustasresourceurl-globally
.filter("trustUrl", ['$sce', function ($sce) {
  return function (url) {
    return $sce.trustAsResourceUrl(url);
  };
}]);



