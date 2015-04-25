module.exports = function (grunt) {
    'use strict';

    var appJs = [
        '<%= buildPath %>/js/jquery.js',
        '<%= buildPath %>/js/angular.js',
        '<%= buildPath %>/js/angular-animate.js',
        '<%= buildPath %>/js/angular-aria.js',
        '<%= buildPath %>/js/angular-ui-router.js',
        '<%= buildPath %>/js/angular-material.js',

        '<%= srcPath %>/js/app.js',
        '<%= srcPath %>/js/**/*.js'
    ];

    var appCss = [
        '<%= buildPath %>/css/angular-material.css',

        '<%= srcPath %>/css/app.css'
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
                 '<%= buildPath %>/js/angular.js',
                 '<%= buildPath %>/js/angular-animate.js',
                 '<%= buildPath %>/js/angular-aria.js',
                 '<%= buildPath %>/js/angular-ui-router.js',
                 '<%= buildPath %>/js/angular-material.js',

                 '<%= buildPath %>/css/angular-material.css'
            ]
        },

        copy: {
            base: {
                files: [
                    {expand: true, cwd: '<%= srcPath %>', src: ['fonts/**'], dest: '<%= buildPath %>/'},
                    {expand: true,
                        cwd: 'bower_components/jquery/dist',
                        src: ['jquery.js'], dest: '<%= buildPath %>/js'},
                    {expand: true,
                        cwd: 'bower_components/angular',
                        src: ['angular.js'], dest: '<%= buildPath %>/js'},
                    {expand: true,
                        cwd: 'bower_components/angular-animate',
                        src: ['angular-animate.js'], dest: '<%= buildPath %>/js'},
                    {expand: true,
                        cwd: 'bower_components/angular-aria',
                        src: ['angular-aria.js'], dest: '<%= buildPath %>/js'},
                    {expand: true,
                        cwd: 'bower_components/angular-ui-router/release',
                        src: ['angular-ui-router.js'], dest: '<%= buildPath %>/js'},
                    {expand: true,
                        cwd: 'bower_components/angular-material',
                        src: ['angular-material.js'], dest: '<%= buildPath %>/js'},

                    {expand: true,
                        cwd: 'bower_components/angular-material',
                        src: ['angular-material.css'], dest: '<%= buildPath %>/css'},

                    {expand: true,
                        cwd: 'bower_components/material-design-icons',
                        src: ['navigation/svg/production/ic_menu_18px.svg'], dest: '<%= buildPath %>/img/icons'}
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
                    sourceMap: false,
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
                sourceMap: false
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
