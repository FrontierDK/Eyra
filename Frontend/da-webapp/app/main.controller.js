// record and submit recordings/data to server

'use strict';

angular.module('daApp')
.controller('MainController', MainController);

MainController.$inject = ['$scope',
                          'recordingService',
                          'tokenService'];

function MainController($scope, recordingService, tokenService) {
  var recCtrl = this; // record control
  var recService = recordingService;

  recCtrl.clearLocalDb = clearLocalDb;
  recCtrl.getTokens = getTokens;
  recCtrl.record = record;
  recCtrl.stop = stop;

  recCtrl.msg = ''; // single debug/information msg
  recCtrl.curRec = recService.currentRecording;

  recCtrl.recordBtnDisabled = false;
  recCtrl.stopBtnDisabled = true;

  var currentToken = {'id':0, 'token':'No token yet. Hit \'Record\' to start'};
  recCtrl.displayToken = currentToken['token'];


  activate();

  //////////

  function activate() {
    // provide updateBindings function so recordingService can 
    // call that function when it needs to update bindings
    recService.init(updateBindingsCallback, recordingCompleteCallback);    
  }

  // dev function, clear the entire local forage database
  function clearLocalDb() {
    if (confirm('Are you sure?\nThis will delete the entire local db, including tokens and recordings.'))
    {
      recCtrl.msg = 'Clearing entire local db...';
      tokenService.clearLocalDb();      
    }
  }

  function getTokens() {
    recCtrl.msg = 'Getting tokens...';

    tokenService.getTokens(25);
  }

  function record() {
    recCtrl.msg = 'Recording now...';

    recCtrl.recordBtnDisabled = true;
    recCtrl.stopBtnDisabled = false;

    recService.record();

    // show token on record/newToken button hit
    tokenService.nextToken().then(function(data){
      recCtrl.displayToken = data['token'];
      currentToken = data;
    });
  }

  // function passed to our recording service, notified when a recording has been finished
  function recordingCompleteCallback() {
    send(); // attempt to send current recording
    // TODO if unsuccessful, save it locally
  }

  function send() {
    recCtrl.msg = 'Sending recs...';

    // these scope variables connected to user input obviously have to be sanitized.
    recService.send(recCtrl.speakerId,
                    recCtrl.isntructorId,
                    recCtrl.deviceId,
                    recCtrl.curLocation,
                    recCtrl.comments,
                    currentToken['id']);
  }

  function stop() {
    recCtrl.msg = 'Processing wav...';

    recCtrl.stopBtnDisabled = true;
    recCtrl.recordBtnDisabled = false;
    
    recService.stop();
  }

  function updateBindingsCallback() {
    $scope.$apply();
  }
}

