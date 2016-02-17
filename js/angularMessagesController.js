app.controller('messagesController', function($scope, $rootScope, $http, $route, $routeParams, $location, dataService) {
    $scope.messages = null;
    $scope.messages2 = null;
    $scope.send = null;
    $scope.user = null;
    $scope.to = $routeParams.id;
    $rootScope.me = me;

    dataService.submitData("", me, $scope.to, "", "", "", "messages-read");

    // user data from profile page
    dataService.getData('profile', $scope.to, '').then(function(dataResponse) {
        $scope.user = dataResponse.data[0];
    });

    // list of conversations - maybe switch to own table later
    dataService.getData('messages', me, '').then(function(dataResponse) {
        $scope.messages = dataResponse.data;
        $scope.unread = 0;
        // count unread messages
        for (i = 0; i < $scope.messages.length; i++) {
            $scope.unread += parseInt($scope.messages[i].unread);
        }
        // add excerpts
        for (i = 0; i < $scope.messages.length; i++) {
            $scope.messages[i].excerpts = $scope.messages[i].words.substring(0, 30) + "...";
        }
    });

    // list of messages within conversation
    dataService.getData('messages2', me, $scope.to).then(function(dataResponse) {
        $scope.messages2 = dataResponse.data;

        // scroll to bottom -- not working right now
        $location.hash('bottom');
        $anchorScroll();
    });

    $scope.pressEnter = function(keyEvent) {
        if (keyEvent.which === 13)
            $scope.messagesSend();
    };

    // update on messages read
    $scope.messagesSend = function(){
        dataService.submitData("", me, $scope.to, $scope.send, "", "", "messages-send");
        $scope.send = "";
    };
});