(function () {
    'use strict';

    var app = angular.module('logdog.app', [
        'ui.router',
        'ui.bootstrap'
    ],
    ['$interpolateProvider', function ($interpolateProvider) {
        $interpolateProvider.startSymbol('[[');
        $interpolateProvider.endSymbol(']]');
    }]);

    app.run(function () {
        $(function() {$.material.init();});
    });

    app.directive('logViewer', [function(){
        return {
            restrict: 'A',
            templateUrl: 'partial/log-viewer.html',
            link: function (scope, element, attrs) {
            }
        }
    }]);

    app.controller('Test', ['$scope', '$timeout', function($scope, $timeout){
        $scope.messages = [{msg: '----'}];

        var reconnectDelay = 1000;

        function initSocket() {
            var socket = window.s = new WebSocket('ws://127.0.0.1:8888/ws/logs');

            socket.onopen = function (event) {
                console.log('socket open');
                reconnectDelay = 1000;
            };

            socket.onmessage = function (event) {
                console.log('socket message');
                $scope.$apply(function () {
                    $scope.messages.unshift({msg: event.data});
                });
            };

            socket.onerror = function (event) {
                console.log('socket error');
            };

            socket.onclose = function (event) {
                console.log('socket close');
                console.log('trying to reconnect...');
                $timeout(initSocket, reconnectDelay);
                reconnectDelay *= 2;
            };
        }

        initSocket();
    }])
})();