/*
Copyright 2016 The Eyra Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

File author/s:
    Matthias Petursson <oldschool01123@gmail.com>
*/

"use strict";

describe('evaluation controller', function(){
  beforeEach(module('daApp'));
  var TYPICALSERVERWAIT = 3000; // ms

  var $rootScope, $controller;
  beforeEach(inject(function(_$rootScope_, _$controller_){
    // The injector unwraps the underscores (_) from around the parameter names when matching
    $rootScope = _$rootScope_;
    $controller = _$controller_;
  }));

  it('should initialize', function(){
    var $scope = {};
    $scope.$watch = function(){};

    var evalCtrl = $controller('EvaluationController', { $scope: $scope });

    expect(typeof(evalCtrl.play)).toBe('function');
    expect(typeof(evalCtrl.skip)).toBe('function');
    expect(evalCtrl.playBtnDisabled).toBeDefined();
    expect(evalCtrl.skipBtnDisabled).toBeDefined();
    expect(typeof(evalCtrl.displayToken)).toBe('string');
    expect(evalCtrl.hidePlayback).toBeDefined();
    expect(typeof(evalCtrl.uttsGraded)).toBe('number');
    expect(typeof(evalCtrl.gradesDelivered)).toBe('number');

    setTimeout(function(){
      expect($rootScope.isLoaded).toBe(true);
    }, TYPICALSERVERWAIT);
  });
});