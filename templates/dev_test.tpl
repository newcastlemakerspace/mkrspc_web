% page_type = "front"
% rebase('templates/mkrspc_front_base.tpl')

<h2 class='page-title'>Dev test page</h2>
<div id='content'>

    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc sollicitudin vestibulum lectus eu ornare. In feugiat tincidunt nunc egestas venenatis. Duis convallis sit amet nulla id sagittis. Donec pulvinar pulvinar hendrerit. Curabitur mollis nisi ut gravida eleifend. Aenean vulputate felis in ex sagittis, id facilisis massa molestie. Duis ante nisi, tincidunt in dolor in, tincidunt eleifend justo.</p>

    <p>Pellentesque condimentum mauris vitae ligula dignissim, id vehicula felis interdum. Donec interdum, urna vel finibus aliquam, felis tellus pretium dolor, et ullamcorper est risus ac lectus. Curabitur accumsan lectus eu justo fermentum, ut aliquet nunc vehicula. Praesent eu est cursus, mollis enim a, luctus massa. Nunc in nisl sit amet magna ultrices malesuada. Aliquam molestie libero sit amet felis efficitur, eget varius justo accumsan. Vivamus imperdiet feugiat nunc id ullamcorper. Suspendisse in eleifend erat. Integer nec massa accumsan mauris sollicitudin lacinia ut non sem. In faucibus mi libero, nec condimentum nisl rutrum ac. Vivamus facilisis enim quis ornare hendrerit. Nullam elementum nisi vitae metus dapibus, eget rhoncus nisl aliquam. Donec pretium tellus tincidunt libero ornare, sed aliquam ipsum porta. Duis nunc quam, mattis ultrices interdum et, ultricies quis lectus. Aliquam auctor eros ac neque sodales, id posuere diam gravida.</p>

    <div class="site-message-error"><i class="fa fa-exclamation-triangle"></i> A terrible error occurred!</div>
    <div class="site-message-success"><i class="fa fa-check-circle"></i> All good.</div>
    <div class="site-message-info"><i class="fa fa-circle-o"></i> The robot insurrection will begin in 1024 seconds.</div>
    <div class="site-message-validation"><i class="fa fa-question-circle"></i> Dunno if that looks right?</div>

    <h3>Change password</h3>
    <div id="form_container">
        <form id="member_login" class="loginform" method="post" action="/change_password">
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

    <h3>Upload image</h3>
    <div id="form_container_2">
        <form action="/image_upload" class="loginform" method="post" enctype="multipart/form-data">
            <ul >
                <li>
                    <label class="description" for="caption">Caption</label>
                    <div>
                        <input class="element text medium" type="text" name="caption" />
                    </div>
                </li>
                <li>
                    <label class="description" for="upload">Select file</label>
                    <div>
                        <input class="element text medium" type="file" name="upload" />
                    </div>
                </li>
                <li class="buttons">
                    <input class="ncms_buttons" type="submit" value="Upload" />
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

