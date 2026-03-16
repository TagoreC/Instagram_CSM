// instagram_cms - main js
// form validation and small ui interactions

$(document).ready(function () {

    // highlight active nav link
    var currentPath = window.location.pathname;
    $('.navbar-nav .nav-link').each(function () {
        if ($(this).attr('href') === currentPath) {
            $(this).addClass('active');
        }
    });

    // set min date on scheduled date input to today
    var today = new Date().toISOString().split('T')[0];
    $('input[type="date"]').attr('min', today);

    // show/hide scheduled date field based on status dropdown
    var statusVal = $('#status').val();
    if (statusVal !== 'scheduled') {
        $('#scheduledDateGroup').hide();
    }
    $('#status').on('change', function () {
        if ($(this).val() === 'scheduled') {
            $('#scheduledDateGroup').show();
        } else {
            $('#scheduledDateGroup').hide();
            $('#scheduled_at').val('');
        }
    });

    // ---- add post form validation ----
    $('#addForm').on('submit', function (e) {
        e.preventDefault();
        var isValid = true;

        // clear old errors first
        $('.field-error').removeClass('field-error');
        $('.error-msg').text('');

        // validate username
        var username = $('#username').val().trim();
        if (username === '') {
            $('#username').addClass('field-error');
            $('#username').next('.error-msg').text('Username is required');
            isValid = false;
        }

        // validate caption
        var caption = $('#caption').val().trim();
        if (caption === '') {
            $('#caption').addClass('field-error');
            $('#caption').next('.error-msg').text('Caption cannot be empty');
            isValid = false;
        }

        // validate image url
        var imgUrl = $('#image_url').val().trim();
        if (imgUrl === '') {
            $('#image_url').addClass('field-error');
            $('#image_url').next('.error-msg').text('Image URL is required');
            isValid = false;
        }

        // if scheduled, check date is filled
        var status = $('#status').val();
        if (status === 'scheduled') {
            var schedDate = $('#scheduled_at').val();
            if (schedDate === '') {
                $('#scheduled_at').addClass('field-error');
                $('#scheduled_at').next('.error-msg').text('Please pick a scheduled date');
                isValid = false;
            }
        }

        // analytics form validation - check if fields exist
        if ($('#followers').length) {
            var followers = $('#followers').val().trim();
            if (followers === '' || isNaN(followers)) {
                $('#followers').addClass('field-error');
                $('#followers').next('.error-msg').text('Followers must be a number');
                isValid = false;
            }

            var following = $('#following').val().trim();
            if (following === '' || isNaN(following)) {
                $('#following').addClass('field-error');
                $('#following').next('.error-msg').text('Following must be a number');
                isValid = false;
            }

            var totalPosts = $('#total_posts').val().trim();
            if (totalPosts === '' || isNaN(totalPosts)) {
                $('#total_posts').addClass('field-error');
                $('#total_posts').next('.error-msg').text('Total posts must be a number');
                isValid = false;
            }
        }

        // console.log(isValid);
        if (isValid) {
            this.submit();
        }
    });

    // ---- comment form validation ----
    $('#actionForm').on('submit', function (e) {
        e.preventDefault();
        let valid = true;

        $('.field-error').removeClass('field-error');
        $('.error-msg').text('');

        // check commenter name
        let commenter = $('#commenter').val().trim();
        if (commenter === '') {
            $('#commenter').addClass('field-error');
            $('#commenter').next('.error-msg').text('Name is required');
            valid = false;
        }

        // check comment body
        let body = $('#body').val().trim();
        if (body === '') {
            $('#body').addClass('field-error');
            $('#body').next('.error-msg').text('Comment cannot be empty');
            valid = false;
        }

        if (valid) {
            $('#submitBtn').html('<span class="spinner-border spinner-border-sm me-1"></span> Posting...');
            $('#submitBtn').prop('disabled', true);
            this.submit();
        }
    });

    // auto submit filter form on status change
    $('#statusFilter').on('change', function () {
        $(this).closest('form').submit();
    });

    // show toast on success page
    if ($('#successToast').length) {
        var toastEl = document.getElementById('successToast');
        var toast = new bootstrap.Toast(toastEl, { delay: 4000 });
        toast.show();
    }

});
