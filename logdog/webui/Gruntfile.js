module.exports = function (grunt) {
    'use strict';

    var appJs = [
        '<%= buildPath %>/js/jquery.js',
        //'<%= buildPath %>/js/bootstrap.js',
        '<%= buildPath %>/js/ripples.js',
        '<%= buildPath %>/js/material.js',

        '<%= buildPath %>/js/angular.js',
        '<%= buildPath %>/js/ui-bootstrap.js',
        '<%= buildPath %>/js/ui-bootstrap-tpls.js',
        '<%= buildPath %>/js/angular-ui-router.js',

        '<%= srcPath %>/js/app.js',
        '<%= srcPath %>/js/**/*.js'
    ];

    var appCss = [
        '<%= buildPath %>/css/bootstrap.css',
        '<%= buildPath %>/css/ripples.css'
    ];

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        buildPath: 'static',
        srcPath: 'assets',

        clean: {
            options: {
                force: true
            },
            build: ['<%= buildPath %>'],
            postMin: [
                '<%= buildPath %>/js/jquery.js',
                '<%= buildPath %>/js/bootstrap.js',
                '<%= buildPath %>/js/ripples.js',
                '<%= buildPath %>/js/material.js',

                '<%= buildPath %>/js/angular.js',
                '<%= buildPath %>/js/ui-bootstrap.js',
                '<%= buildPath %>/js/ui-bootstrap-tpls.js',
                '<%= buildPath %>/js/angular-ui-router.js',

                '<%= buildPath %>/css/bootstrap.css',
                '<%= buildPath %>/css/bootstrap.css.map',
                '<%= buildPath %>/css/ripples.css',
                '<%= buildPath %>/css/ripples.css.map'
            ]
        },

        copy: {
            base: {
                files: [
                    {expand: true, cwd: '<%= srcPath %>', src: ['fonts/**'], dest: '<%= buildPath %>/'},
                    {expand: true,
                        cwd: 'bower_components/bootstrap-material-design/dist',
                        src: [
                            'css/ripples.css',
                            'css/ripples.css.map',
                            'css/material-wfont.min.css', // !important
                            'css/material-wfont.min.css.map', // !important
                            'fonts/**',
                            '!fonts/LICENSE.txt',
                            'js/ripples.js',
                            'js/material.js'
                        ],
                        dest: '<%= buildPath %>/'},
                    {expand: true,
                        cwd: 'bower_components/bootstrap/dist',
                        src: [
                            'css/bootstrap.css',
                            'css/bootstrap.css.map',
                            'js/bootstrap.js'
                            ], dest: '<%= buildPath %>/'},
                    {expand: true,
                        cwd: 'bower_components/angular',
                        src: ['angular.js'], dest: '<%= buildPath %>/js'},
                    {expand: true,
                        cwd: 'bower_components/jquery/dist',
                        src: ['jquery.js'], dest: '<%= buildPath %>/js'},
                    {expand: true,
                        cwd: 'bower_components/angular-bootstrap',
                        src: ['ui-bootstrap.js', 'ui-bootstrap-tpls.js'], dest: '<%= buildPath %>/js'},
                    {expand: true,
                        cwd: 'bower_components/angular-ui-router/release',
                        src: ['angular-ui-router.js'], dest: '<%= buildPath %>/js'}
                ]
            }
        },

        concat: {
            dev: {
                files: {
                    '<%= buildPath %>/css/app.css': appCss,
                    '<%= buildPath %>/js/app.js': appJs
                }
            }
        },

        uglify: {
            prod: {
                options: {
                    mangle: true,
                    except: ['jQuery', 'angular'],
                    sourceMap: true,
                    sourceMapName: '<%= buildPath %>/js/app.js.map'
                },
                files: {
                    '<%= buildPath %>/js/app.js': appJs
                }
            }
        },

        cssmin: {
            options: {
                shorthandCompacting: false,
                roundingPrecision: -1,
                sourceMap: true
            },
            prod: {
                files: {
                    '<%= buildPath %>/css/app.css': appCss
                }
            }
        },

        watch: {
            configFiles: {
                files: ['Gruntfile.js'],
                tasks: ['dev'],
                options: {
                    reload: true
                }
            },
            javascript: {
                files: ['<%= srcPath %>/**/*.js'],
                tasks: ['dev']
            },
            less: {
                files: '<%= srcPath %>/**/*.less',
                tasks: ['dev']
            },
            templates: {
                files: ['<%= srcPath %>/**'],
                tasks: ['dev']
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-watch');

    var dev = [
        'clean:build',
        'copy:base',

        'concat:dev'
    ];
    var prod = [
        'clean:build',
        'copy:base',

        'uglify:prod',
        'cssmin:prod',
        'clean:postMin'
    ];

    grunt.registerTask('dev', dev);
    grunt.registerTask('prod', prod);
};
