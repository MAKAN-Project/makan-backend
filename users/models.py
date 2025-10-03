from django.db import models
import re
class UserManager(models.Manager):
    
    def user_validator(self, postData):
        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+$')

        if not postData['first_name']:
            errors["missing_first_name"] = "Please Enter a First name"
        elif len(postData['first_name']) < 2:
            errors['first_name_length'] = "First name should be at least 2 characters"

        if not postData['last_name']:
            errors["missing_last_name"] = "Please Enter a Last name"
        elif len(postData['last_name']) < 2:
            errors['last_name_length'] = "Last name should be at least 2 characters"

        if not postData['email']:
            errors["missing_field_email"] = "Please Enter an email"
        elif not EMAIL_REGEX.match(postData['email']):
            errors['email'] = "Invalid email address"
        elif User.objects.filter(email=postData['email']).exists():
            errors['email_exists'] = "Email already registered"

        password = postData.get('password')
        confirm_pw = postData.get('confirm_password')
        if not password or not confirm_pw:
            errors["missing_field_password"] = "Please enter password and confirm it"
        elif len(password) < 8:
            errors['password_length'] = "Password should be at least 8 characters"
        elif password != confirm_pw:
            errors['password_mismatch'] = "Password and Confirm Password do not match"

        if not postData.get('phone'):
            errors["missing_phone"] = "Please enter a phone number"
        elif not postData['phone'].isdigit():
            errors["invalid_phone"] = "Phone number should contain digits only"
        elif len(postData['phone']) != 11:  
            errors["phone_length"] = "Phone number should be 11 digits long"

        if not postData['address']:
            errors["missing_address"] = "Please Enter an address"
        elif len(postData['address']) < 2:
            errors['address_length'] = "Address should be at least 2 characters"

        return errors

class User(models.Model):
    ROLE_CHOICES = (
            ('admin', 'Admin'),
    ('customer', 'Customer'),
    ('engineer', 'Engineer'),
    )
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    email = models.CharField(max_length=45)
    password = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, null=True, blank=True)   # ✅ أضفت الهاتف
    address = models.CharField(max_length=255, null=True, blank=True) # ✅ أضفت العنوان
    role = models.CharField(max_length=45,default="Customer")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
