$(function () {
    'use strict';

    // TODO: Make this pretty, not two identical functions.

    var $new_course_btn = $('.new-course-btn');
    var $new_course_name = $('.new-course-name');

    var $courses = $('.courses');

    $("select").select2();

    // TODO: the following was only used in the old creation form, upload.htm
    // Unless we someday want to create courses and educations using AJAX, this code can be removed
    $new_course_btn.click(function (e) {
        e.preventDefault();

        utils.forms.button_loading($new_course_btn);

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

    var $new_education_btn = $('.new-education-btn');
    var $new_education_name = $('.new-education-name');
    var $new_education_degree = $('.new-education-degree');

    var $educations = $('.educations');

    $new_education_btn.click(function (e) {
        e.preventDefault();

        utils.forms.button_loading($new_education_btn);

        var education_name = $new_education_name.val();
        var education_degree_id = $new_education_degree.val();

        // TODO: temporary make this work again, as the hidden selector
        // did not work
        if(education_degree_id === "" | !isFinite(education_degree_id))
           education_degree_id = 1;

        $.post('/examination/api/education/',
            {education_name: education_name, degree_id: education_degree_id},
            function (data) {
                //$new_education_name.val('');
                //$new_education_degree.find('option:selected').prop('selected',
                    //false);

                //var education_id = data.education_id;
                //var educations = data.educations;

                //$educations.empty();

                //_.forEach(educations, function (education) {
                    //var $option = $('<option></option>');
                    //$option.val(education.id);
                    //$option.text(education.name);

                    //if (education.id == education_id) {
                        //$option.prop('selected', true);
                    //}

                    //$educations.append($option);
                //});

                clearflash();
                flash('Opleiding succesvol toegevoegd', 'success');
            }).fail(function (resp) {
                var message = 'Er is iets misgegaan, =(';
                if (resp.responseJSON) {
                    message = resp.responseJSON.error;
                }

                clearflash();
                flash(message, 'danger');
            }).always(function () {
                $new_education_btn.button('reset');
            });
    });
});
