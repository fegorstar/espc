$(document).ready(function() {
    // Handle form submission
    $('#login-form').on('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission
        
        // Show loader and disable button
        $('#login-button').prop('disabled', true).text('Logging in...');
        
        // Prepare the data
        var email = $('input[name="email"]').val();
        var password = $('input[name="password"]').val();
        
        // Perform AJAX request
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: {
                email: email,
                password: password,
                csrfmiddlewaretoken: '{{ csrf_token }}'
            },
            success: function(response) {
                if (response.status === 200) {
                    // Save tokens and user data to local storage
                    localStorage.setItem('access_token', response.data.tokens.access);
                    localStorage.setItem('refresh_token', response.data.tokens.refresh);
                    localStorage.setItem('first_name', response.data.first_name);
                    localStorage.setItem('last_name', response.data.last_name);
                    localStorage.setItem('email', response.data.email);
                    localStorage.setItem('user_type', response.data.user_type);
                    localStorage.setItem('profile_picture', response.data.profile_picture);
                    localStorage.setItem('state', response.data.state);
                    localStorage.setItem('city', response.data.city);
                    
                    // Redirect to dashboard
                    window.location.href = '/api/v1/auth/dashboard/'; 
                } else {
                    // Display error message
                    $('#error-message').text(response.message).show().delay(5000).fadeOut(); // Show error and fade out after 5 seconds
                }
            },
            error: function(xhr) {
                // Display specific error message from server
                var errorMessage = xhr.responseJSON && xhr.responseJSON.message ? xhr.responseJSON.message : 'An error occurred. Please try again.';
                $('#error-message').text(errorMessage).show().delay(5000).fadeOut(); // Show error and fade out after 5 seconds
            },
            complete: function() {
                // Hide loader and enable button
                $('#login-button').prop('disabled', false).text('Login');
            }
        });
    });
});

$(document).ready(function() {
    // Handle form submission
    $('#register-form').on('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        // Get form values
        var firstName = $('input[name="first_name"]').val();
        var lastName = $('input[name="last_name"]').val();
        var email = $('input[name="email"]').val();
        var password = $('input[name="password"]').val();
        var confirmPassword = $('input[name="confirm_password"]').val();
        
        // Check if passwords match
        if (password !== confirmPassword) {
            $('#error-message').text('Passwords do not match.').show().delay(5000).fadeOut(); // Show error and fade out after 5 seconds
            return; // Prevent form submission
        }
        
        // Show loader and disable button
        $('#register-button').prop('disabled', true).text('Registering...');
        
        // Perform AJAX request
        $.ajax({
            url: $(this).attr('action'),
            type: 'POST',
            data: {
                first_name: firstName,
                last_name: lastName,
                email: email,
                password: password,
                confirm_password: confirmPassword,
                csrfmiddlewaretoken: '{{ csrf_token }}'
            },
            success: function(response) {
                if (response.status === 201) {
                    // Show success message
                    $('#error-message').removeClass('text-danger').addClass('text-success').text(response.message).show().delay(5000).fadeOut(function() {
                        // Redirect to login after showing message
                        window.location.href = '/api/v1/auth/signin/'; 
                    });
                } else {
                    // Display error message
                    $('#error-message').text(response.message).show().delay(5000).fadeOut(); // Show error and fade out after 5 seconds
                }
            },
            error: function(xhr) {
                // Display error message
                var errorMessage = xhr.responseJSON && xhr.responseJSON.error ? xhr.responseJSON.error : 'An error occurred. Please try again.';
                $('#error-message').text(errorMessage).show().delay(5000).fadeOut(); // Show error and fade out after 5 seconds
            },
            complete: function() {
                // Hide loader and enable button
                $('#register-button').prop('disabled', false).text('Sign Up');
            }
        });
    });
});


