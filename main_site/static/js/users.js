var User = function(args) {
    self = this;
    self.username = args.username;
    self.password = args.password;
    self.region = args.region;
    self.admin = args.admin;
    return self;
};

(function() {

usersModel = (function () {
    var self = this;

    self.users = ko.observableArray([]);
    self.loadingUsers = ko.observable(false);
    self.numberOfUsers = ko.observable(0);
    self.selectedUser = ko.observable();

    self.loadUsers = function() {
        self.loadingUsers(true);
        self.numberOfUsers(0);
        ajaxParams = {
            url: loadUsersURL,
            type: 'GET', 
            success: self.usersCallback,
            error: self.usersCallbackError
        };
        return $.ajax(ajaxParams);
    };

    self.usersCallback = function(response) {
        var users, user;
        users = response.users;
        self.users([]);
        for(i = 0; i < users.length; i++){
            user = new User(users[i]);
            self.users.push(user);
        }
        self.numberOfUsers(users.length);
        self.loadingUsers(false);
    };

    self.usersCallbackError = function(response) {
        self.users([]);
        self.numberOfUsers(0);
        self.loadingUsers(false);
    };

    self.addUser = function() {
        data = {username: $('#username').val(), 
                password: $('#password').val(), 
                region: $('#region').val(), 
                admin: $('#admin').is(':checked')
                };
        ajaxParams = {
            url: addUsersURL,
            type: 'POST',
            data: JSON.stringify(data),
            contentType: 'appliction/json;',
            success: function(response) {
                if (response.results === 'success')
                {
                    $('#username').val('');
                    $('#password').val('');
                    $('#region').val('');
                    $('#admin').prop('checked', false);
                    self.users.push(new User(data));
                }
                else
                    alert(response.message);
            }
        };
        return $.ajax(ajaxParams);   
    };

    self.selectUser = function() {
        self.selectedUser(this);
    };

    self.modifySelectedUser = function() {
        data = {username: self.selectedUser().username, 
                password: $('#edit-password').val(), 
                region: $('#edit-region').val(), 
                admin: $('#edit-admin').is(':checked')
                };
        ajaxParams = {
            url: editUsersURL,
            type: 'POST',
            data: JSON.stringify(data),
            contentType: 'appliction/json;',
            success: function(response) {
                if (response.results === 'success')
                {
                    $('#username').val('');
                    $('#edit-password').val('');
                    $('#edit-region').val('');
                    $('#edit-admin').prop('checked', false);
                    self.users.replace(self.selectedUser(), new User(data));
                    self.selectedUser(null);
                }
            }
        };
        return $.ajax(ajaxParams);        
    }

    self.deleteSelectedUser = function() {
        data = {username: self.selectedUser().username};
        ajaxParams = {
            url: deleteUserURL,
            type: 'POST',
            data: JSON.stringify(data),
            contentType: 'appliction/json;',
            success: function(response) {
                if (response.results === 'success')
                {
                    self.users.remove(self.selectedUser());
                    self.selectedUser(null);
                }
            }
        };
        return $.ajax(ajaxParams);
    };
})
}).call(this);