# TODO: Unify User Registration Logic

## Tasks
- [x] Update app.py: Modify /register route to use AddUserForm for validation, add initial deposit check, and handle form errors by flashing and redirecting.
- [x] Update templates/login.html: Change registration form to use WTForms rendering (e.g., {{ reg_form.name(class="form-control") }}), add error display, and ensure form action remains /register.
- [x] Update app.py: Modify /login route to pass reg_form = AddUserForm() to the template for rendering.
- [x] Test admin add user form: Ensure it still works correctly after changes.
- [x] Test user registration form: Ensure it validates, saves data, and flashes success message.
- [x] Verify both forms save data using the same User model logic (generate account number, create user, save to DB).
