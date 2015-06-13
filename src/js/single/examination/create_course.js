$(function () {
    'use strict';

    var $new_course_btn = $('.new-course-btn');
    var $new_course_name = $('.new-course-name');

    var $courses = $('.courses');

    $new_course_btn.click(function (e) {
        e.preventDefault();

        $new_course_btn.button('loading');

        var course_name = $new_course_name.val();

        $.post('/examination/api/course/', {course_name: course_name},
            function (data) {
                $new_course_name.val('');

                var course_id = data.course_id;
                var courses = data.courses;

                $courses.empty();

                _.forEach(courses, function (course) {
                    var $option = $('<option></option>');
                    $option.val(course.id);
                    $option.text(course.name);

                    if (course.id == course_id) {
                        $option.prop('selected', true);
                    }

                    $courses.append($option);
                });

                clearflash();
                flash('Vak succesvol toegevoegd', 'success');
            }).fail(function (resp) {
                var message = 'Er is iets misgegaan, =(';
                if (resp.responseJSON) {
                    message = resp.responseJSON.error;
                }

                clearflash();
                flash(message, 'danger');
            }).always(function () {
                $new_course_btn.button('reset');
            });
    });
});
