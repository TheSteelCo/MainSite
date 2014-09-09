function clientLoginModel() {
	var self = this;

	self.loginDisplay = ko.observable(0);
	self.userEmail = ko.observable('');
	self.userPassword = ko.observable('');
	self.newPassword = ko.observable('');
	self.confirmPassword = ko.observable('');

	self.loginError = ko.observable(false);
	self.loginErrorText = ko.observable('');

	self.passwordRecovery = function()
	{
		self.loginDisplay(1);
	};

	self.login = function()
	{
		self.loginError(false);
		self.loginErrorText('');
		if(self.userEmail() == ''){
			self.loginError(true);
			self.loginErrorText('Please enter an email address');
			return;
		}
		if(document.getElementById("login-form").checkValidity() === false){
			self.loginError(true);
			self.loginErrorText('Invalid Email. Please check and try again.');
			return;
		}
		if(self.userPassword() == ''){
			self.loginError(true);
			self.loginErrorText('Please enter a password');
			return;
		}
		if(self.userPassword().length < 8){
			self.loginError(true);
			self.loginErrorText('Invalid Password');
			self.userPassword('');
			return;
		}
		window.location.href = MAIN_PAGE;
	};

	self.resetPassword = function()
	{
		self.loginError(false);
		self.loginErrorText('');
		if(self.userEmail() == ''){
			self.loginError(true);
			self.loginErrorText('Please enter an email address');
			return;
		}
		if(document.getElementById("login-form").checkValidity() === false){
			self.loginError(true);
			self.loginErrorText('Invalid Email. Please check and try again.');
			return;
		}
		alert('email sent!');
	}

	self.saveNewPassword = function()
	{
		self.loginError(false);
		self.loginErrorText('');
		if (self.newPassword().length < 8){
			self.loginError(true);
			self.loginErrorText('Password must be at least 8 characters long');
			self.newPassword('');
			self.confirmPassword('');
			return;
		}
		if (self.newPassword() != self.confirmPassword()){
			self.loginError(true);
			self.loginErrorText('Passwords do not match!');
			self.newPassword('');
			self.confirmPassword('');
			return;
		}
		alert('Password Reset!');
	}
}