Adding a new newsletter release
################################
:summary: This documents how a new newsletter release can be added to the website.
:resource: Memberclicks
:difficulty: Easy
:permissions required: Admin login

Step 1: Obtain Newsletter from Board member in-charge
---------------------------------------------------------

A member of the OCNS Board is in-charge of the news letter and will get in
touch with the webmasters when a new version is ready to be disseminated.
They will provide a file (PDF) that needs to be added to the website.

When obtained, save the file continuing the naming scheme. Usually it is:
:code:`<PERIOD> <YEAR> Volume <volume number> No <issue number>.pdf`


Step 2: Upload Newsletter file
-------------------------------

#. Access "Media Manager": Website > Media Manager.
#. Navigate to the "newsletter" folder in the left hand side bar: Media > docs > newsletter.
#. Choose and upload the new file.

Step 3: Update the newsletter article page
-------------------------------------------

The newsletter article page on the website at https://www.cnsorg.org/newsletter
needs to be updated to list the new newsletter.

#. Access the "Newsletter" article page: Website > Article Manager > Newsletter (search Newsletter in the search box if needed).

   #. Click the entry to go to the Edit page.

#. Click in the text area.
#. Obtain the link to the newsletter file:

   #. Click "site links" at the bottom of the page.
   #. Navigate to docs > newsletter.
   #. Select the new newsletter by clicking on the "link" icon.
   #. Click "Insert link".

#. Click "Toggle Editor" to change the editor to HTML mode.
#. Move previous newsletter to the list under "Previous newsletters"

   #. Add a new list item using the HTML :code:`<li>` tag at the start of the list.
   #. Copy the value of the :code:`data=` field of the :code:`<object>` tag.
   #. Use this for the :code:`href=` field in the new list item.
   #. Add text for the link.

#. Add new newsletter:

   #. To make the new newsletter available using the browser's PDF reader, Replace the contents of the :code:`data=` field of the :code:`<object>` tag with the link of the new newsletter obtained in step 3.
   #. To place a link for browsers that do not support PDF reading, replace the contents of the :code:`href=` field of the :code:`<a>` tag with the link of the new newsletter obtained in step 3.

#. Delete the line inserted by "Site links" in step 3.
#. Use "Toggle Editor" to preview your changes.
#. If everything is OK, click the "Save" button in the top right hand corner to
   save your changes.

Step 4: Double check
--------------------

#. Navigate to https://www.cnsorg.org/newsletter to check the page. You may
   need to refresh the page a few times to view the latest version.
