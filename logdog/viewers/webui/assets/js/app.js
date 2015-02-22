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

    app.directive('logViewer', ['$timeout', function($timeout){
        return {
            restrict: 'A',
            scope: {socket: '='},
            templateUrl: 'partial/log-viewer.html',
            link: function (scope, element, attrs) {
                var logContainer = element.find('#id-log-lines');
                var el = element[0];
                var buffer = [];

                scope.socket.on(scope.socket.events.MSG, function(event){
                    buffer.push(event.data);
                });

                var dumpInterval = 100;
                function dumpLog(){
                    if (buffer.length) {
                        var buf = buffer;
                        buffer = [];
                        logContainer.append(buf.join(''));
                        el.scrollTop = el.scrollHeight;
                    }
                    $timeout(dumpLog, dumpInterval);
                }

                $timeout(dumpLog, dumpInterval);
            }
        }
    }]);

    app.service('Socket', ['$timeout', function ($timeout) {
        return function (url, reconnectDelay) {
            var callbacks = {
                'open': [],
                'message': [],
                'error': [],
                'close': []
            };

            var events = {
                'OPEN': 'open',
                'MSG': 'message',
                'ERR': 'error',
                'CLOSE': 'close'
            };

            var handleEvent = function (type, event) {
                angular.forEach(callbacks[type], function (callback) {
                    callback(event);
                });
            };

            var ws = null;

            reconnectDelay = reconnectDelay || 1000;
            function initSocket() {
                ws = new WebSocket(url);

                ws.onopen = function (event) {
                    console.log('socket open');
                    handleEvent(events.OPEN, event);
                    reconnectDelay = 1000;
                };

                ws.onmessage = function (event) {
                    console.log('socket message');
                    handleEvent(events.MSG, event);
                };

                ws.onerror = function (event) {
                    console.log('socket error');
                    handleEvent(events.ERR, event);
                };

                ws.onclose = function (event) {
                    console.log('socket close');
                    console.log('trying to reconnect...');
                    handleEvent(events.CLOSE, event);
                    $timeout(initSocket, reconnectDelay);
                    reconnectDelay *= 2;
                };

                return ws;
            }

            return {
                'events': events,
                'ws': initSocket(),
                'on': function(eventType, cb){
                    callbacks[eventType].push(cb);
                },
                'off': function(eventType){
                    delete callbacks[eventType];
                }
            }

        };
    }]);

    app.controller('LogViewCtl', ['$scope', 'Socket', function($scope, Socket){
        $scope.socket = Socket('ws://' + location.host + '/ws/logs');
    }]);
})();