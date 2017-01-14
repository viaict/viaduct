function get_global_file_names() {
    var start = ['jquery.js',
        'bootstrap.min.js',
        'jquery-ui-1.10.4.custom.min.js',
        'jquery.dataTables.min.js',
        'dataTables.bootstrap.js',
        'angular.min.js'
    ];

    start.push('*');

    start = start.map(function (f) {return 'src/js/global/' + f;});

    var end = [
        'custom.js',
        'footer.js',
        'textarea.js',
    ];

    for (var i = 0; i < end.length; i++) {
        var filename = 'src/js/global/' + end[i];
        start.push('!' + filename);
        start.push(filename);
    }

    return start;
}

function set_base_path(path, arr) {
    return arr.map(function(f) {return path + f;});
}

module.exports = function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        concat: {
            options: {
                seperator: ';'
            },

            global: {
                src: get_global_file_names(),
                dest: 'dist/js/concat/global.js'
            },

            custom_form_view_results: {
                src: set_base_path('src/js/custom_form/view_results/',
                                   ['has_paid.js', '*']),
                dest: 'dist/js/concat/custom_form/view_results.js'
            },

            single: {
                files: [{
                    expand: true,
                    cwd: 'src/js/single',
                    src: ['**/*.js'],
                    dest: 'dist/js/concat',
                    ext: '.js',
                    extDot: 'last',
                }],
            },

        },

        uglify: {
            all: {
                files: [{
                    expand: true,
                    cwd: 'dist/js/concat',
                    src: ['**/*.js'],
                    dest: 'dist/js/min',
                }],
            },

        },

        copy: {
            dev: {
                files: [{
                    expand: true,
                    cwd: 'dist/js/concat/',
                    src: ['**'],
                    dest: 'app/static/js'
                }]
            },

            prod: {
                files: [{
                    expand: true,
                    cwd: 'dist/js/min/',
                    src: ['**'],
                    dest: 'app/static/js'
                }]
            },
        },

        clean: {
            served_files: 'app/static/js',
            dist: 'dist',
        },

        watch: {
            global: {
                files: 'src/js/global/**/*.js',
                tasks: ['concat:global', 'copy:dev'],
            },

            educations_global: {
                files: 'src/js/educations/global/*.js',
                tasks: ['concat:educations_global', 'copy:dev'],
            },

            educations_list: {
                files: 'src/js/educations/list/*.js',
                tasks: ['concat:educations_list', 'copy:dev'],
            },

            educations_info: {
                files: 'src/js/educations/info/*.js',
                tasks: ['concat:educations_info', 'copy:dev'],
            },

            locations_single: {
                files: 'src/js/locations/single/*.js',
                tasks: ['concat:locations_single', 'copy:dev'],
            },

            schedule_week: {
                files: 'src/js/schedule/week/*.js',
                tasks: ['concat:schedule_week', 'copy:dev'],
            },

            single: {
                files: 'src/js/single/**/*.js',
                tasks: ['concat:single', 'copy:dev'],
            },

        }
    });

    grunt.event.on('watch', function(action, filepath, target) {
          grunt.log.writeln(target + ': ' + filepath + ' has ' + action);
    });

    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-watch');

    grunt.registerTask('prod', ['concat', 'uglify', 'copy:prod']);
    grunt.registerTask('dev', ['concat', 'copy:dev']);
};
