/* profileController.js
Controller script of profile page an AngularJS dating site app. Automatically track visits, add favorites, and update profile info.
*/

app.controller('profileController', function($scope, $http, $route, $routeParams, dataService) {
	$scope.reelies = null;
	$scope.user = null;
	$scope.errors = [];
	$scope.msgs = [];
	$scope.me = me;
	$scope.iframe = null;
	$scope.editorEnabled = false;

	// either visiting a profile, or viewing your own
	if ($routeParams.id)
		$scope.id = $routeParams.id;
	else
		$scope.id = me;

	// get user profile data
	dataService.getData('profile', $scope.id, '').then(function(dataResponse) {
		$scope.user = dataResponse.data[0];

		// track user visiting profile
		dataService.submitData("", me, $scope.id, "", "", "", "profile-visited");
	});

	// get featured reelies in profile
	dataService.getData('profile-reelies', $scope.id, '').then(function(dataResponse) {
		$scope.reelies = dataResponse.data;
	});

	// for trending reelies on left side bar
	dataService.getData('trending', '', '').then(function(dataResponse) {
		$scope.trending = dataResponse.data;
	});

	// enable editor
	$scope.edit = function() {
		if ($scope.editorEnabled === false) {
			$scope.editorEnabled = true;
		} else {
			$scope.editorEnabled = false;

			// update user profile
			dataService.submitData($scope.user.id, $scope.user.username, "", $scope.user.bio, "", "", "profile-update");
		}
	};

	// add to favorites
	$scope.profileFavorited = function() {
		dataService.submitData("", me, $scope.user.id, "", "", "", "profile-favorited");
	};

	// for featured videos
	$scope.showVideo = function(i) {
		$scope.iframe = "index.php/player?id=" + i;
	};

});