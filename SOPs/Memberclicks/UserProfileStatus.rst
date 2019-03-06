User Profile Statuses
----------------------

A user profile may have various statuses:

- Valid/Invalid: represents whether the account has been checked and correct.
  Initially when a new profile is created, it is created as invalid and must be
  manually set to valid by the registration manager.

- Active/Inactive: A profile is active when the dues has been paid (or
  considered as paid).  When the period that the dues have been paid for
  finishes (expires), the system automatically sets the profile to inactive.

When a user profile has been marked inactive, the user will not be able to
login. They can only access the "Membership Dues" form to pay their dues. This
will activate their profile and permit them to login.  So for queries where
users are unable to login, they should be directed to the Membership Dues form.


References
===========

- https://classic.memberclicks.com/hc/en-us/articles/360016120732-Configuring-the-Expiration-Date-Attribute
