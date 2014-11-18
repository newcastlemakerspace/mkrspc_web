% page_type = "front"
% rebase('templates/mkrspc_front_base.tpl')

<h2 class='page-title'>User profile - {{user_name}}</h2>
<div id='content'>
    <p>
        Hi {{user_name}}, this is your user page.
    </p>
    <h3>Change password</h3>
    <div id="form_container">
        <form id="member_login" class="loginform"  method="post" action="/change_password">
        <ul >
            <li>
                <label class="description" for="old_password">Old password</label>
                <div>
                    <input id="old_password" name="old_password" class="element text medium" type="password" maxlength="255" value=""/>
                </div>
            </li>
            <li>
                <label class="description" for="new_password">New password</label>
                <div>
                    <input id="new_password" name="new_password" class="element text medium" type="password" maxlength="255" value=""/>
                </div>
            </li>
            <li>
                <label class="description" for="confirm_new_password">Re-type new password</label>
                <div>
                    <input id="confirm_new_password" name="confirm_new_password" class="element text medium" type="password" maxlength="255" value=""/>
                </div>
            </li>
            <li class="buttons">
                <input type="hidden" name="form_id" value="456567" />
                <input id="saveForm" class="ncms_buttons" type="submit" name="submit" value="Change" />
            </li>
        </ul>
        </form>
    </div>
    <h3>Wiki Edit History (WIP)</h3>
    <table width="100%">
        <tr><th width="12.5%">Timestamp</th><th width="20%">Page</th><th width="12.5%">Action</th><th width="*">Comment</th></tr>
        <tr><td>2015-03-13</td><td>Aardvarks</td><td>Create page</td><td>...</td></tr>
        <tr><td>2015-05-06</td><td>Badgers</td><td>Edit page</td><td>...</td></tr>
        <tr><td>2015-06-22</td><td>Zebras</td><td>Create page</td><td>...</td></tr>
    </table>

</div>

