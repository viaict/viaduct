angular
    .module('pimpyApp',
        ['angular.filter', 'ui.router', 'ngMaterial', 'ngResource'])
    .config(config)
    .factory('ResourceService', ResourceService)
    .controller('FilterController', FilterController)
    .controller('TaskListController', TaskListController)
    .controller('TaskEditController', TaskEditController);

// .controller('MinuteListController', MinuteListController)
// .controller('MinuteEditController', MinuteEditController);

config.$inject = [
    '$interpolateProvider',
    '$urlRouterProvider',
    '$stateProvider',
    '$resourceProvider',
];


function config($interpolateProvider, $urlRouterProvider, $stateProvider,
    $resourceProvider) {
        "use strict";

        $interpolateProvider.startSymbol('{a');
        $interpolateProvider.endSymbol('a}');

        $resourceProvider.defaults.stripTrailingSlashes = false;

        $urlRouterProvider.otherwise("/tasks");

        $stateProvider.state('pimpy', {
            absolute: true,
            controller: 'FilterController',
            controllerAs: 'filterVm',
            templateUrl: Flask.url_for('apimpy.angular', {
                template: 'filter.htm'
            }),
        });

        $stateProvider.state('pimpy.tasks', {
            controller: 'TaskListController',
            controllerAs: 'taskVm',
            templateUrl: Flask.url_for('apimpy.angular', {
                template: 'tasks.htm'
            }),
            url: '/tasks',
        });

        $stateProvider.state('pimpy.taskedit', {
            controller: 'TaskEditController',
            controllerAs: 'taskVm',
            params: {
                task_id: null
            },
            templateUrl: Flask.url_for('apimpy.angular', {
                template: 'task_create.htm'
            }),
            url: '/task/create',
        });

        // $stateProvider.state('pimpy.minutes', {
        //     controller: 'MinuteListController',
        //     controllerAs: 'minVm',
        //     templateUrl: Flask.url_for('apimpy.angular', {
        //         template: 'minutes.htm'
        //     }),
        //     url: '/minutes',
        // });
        //
        // $stateProvider.state('pimpy.minutecreate', {
        //     controller: 'MinuteEditController',
        //     controllerAs: 'minVm',
        //     templateUrl: Flask.url_for('apimpy.angular', {
        //         template: 'minute_create.htm'
        //     }),
        //     url: '/minute/create',
        // });
}

FilterController.$inject = ['$http'];
function FilterController($http) {
    "use strict";

    var vm = this;
    vm.groups = [];
    vm.filter = {};
    vm.setFilter = setFilter;
    vm.isChecked = isChecked;
    vm.isIndeterminate = isIndeterminate;
    vm.toggleAll = toggleAll;
    vm.fabOpen = false;

    activate();

    function activate() {
        $http.get(Flask.url_for('apimpy.groups')).then(
            function(response) {
                vm.groups = response.data;
                for (var key in vm.groups) {
                    vm.filter[vm.groups[key]] = true;
                }
            }
        );
    }

    function isIndeterminate() {
        var allFalse = Object.keys(vm.filter).every(
            function(k) { return !vm.filter[k]; }
        );

        return (!allFalse && !isChecked());
    }

    function isChecked() {
        return Object.keys(vm.filter).every(
            function(k) { return vm.filter[k]; }
        );
    }

    function toggleAll() {
        var bool = !isChecked();
        angular.forEach(vm.filter, function(val, key) {
            vm.filter[key] = bool;
        });
    }

    function setFilter(bool) {
        angular.forEach(vm.filter, function(val, key) {
            vm.filter[key] = bool;
        });
    }
}

ResourceService.$inject = ['$resource'];
function ResourceService($resource) {
    "use strict";

    return {
        Task: $resource(Flask.url_for('apimpy.tasks') + ':id/',
            {id: '@id'}),
        // Minute: $resource(Flask.url_for('apimpy.minutes') + ':id/',
        //     {id: '@id'}),
    };
}

TaskListController.$inject = ['$http', 'ResourceService'];
function TaskListController($http, ResourceService) {
    "use strict";
    var vm = this;
    vm.tasks = [];

    activate();

    function activate() {
        $http.get(Flask.url_for('apimpy.tasks')).then(
            function(response) {
                vm.tasks = response.data;
                console.log(vm.tasks);
            }
        );
    }

    // TODO
    function update_status(id, new_status) {
        var task = ResourceService.Task.get({id: id});
        gask.status = new_status;
        task.$save();
    }
}

TaskEditController.$inject = ['$http', '$stateParams', 'ResourceService'];
function TaskEditController($http, $stateParams, ResourceService) {
    "use strict";
    var vm = this;
    vm.task = {};
    vm.task_id = null;

    activate();

    function activate() {
        if ($stateParams.task_id) {
            vm.task_id = $stateParams.task_id;
            console.log(vm.task_id);
            $http.get(Flask.url_for('apimpy.get_task', {task_id:vm.task_id})).then(
                function(response) {
                    vm.task = response.data;
                }
            );
        }

    }
}
//
// MinuteListController.$inject = ['$http'];
// function MinuteListController($http) {
//     "use strict";
//     var vm = this;
//     vm.tasks = [];
//
//     activate();
//
//     function activate() {
//         $http.get(Flask.url_for('apimpy.tasks')).then(
//             function(response) {
//                 vm.tasks = response.data;
//                 console.log(vm.tasks);
//             }
//         );
//     }
// }
//
// MinuteEditController.$inject = ['$http'];
// function MinuteEditController($http) {
//     "use strict";
//     var vm = this;
//     vm.task = {};
//
//     activate();
//
//     function activate() {
//         $http.get(Flask.url_for('apimpy.task')).then(
//             function(response) {
//                 vm.tasks = response.data;
//                 console.log(vm.tasks);
//             }
//         );
//     }
// }
