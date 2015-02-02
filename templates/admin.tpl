% page_type = "front"
% rebase('templates/mkrspc_front_base.tpl')

<h2 class='page-title'>Site Administration</h2>
<div id='content'>
    <p>Hi there, superuser.</p>
</div>

<h4 class='page-title'>Run backup</h4>
<div id='backup'>
    <div id="backup_form_container">
        <form action="/admin_do_backup" class="wiki-form" method="get">
            <ul>
                <li>
                    <input class="ncms_buttons" type="submit" value="Backup"
                    name="Submit" id="backup_frm_submit" />
                </li>
            </ul>
        </form>
    </div>
</div>

<h4 class='page-title'>Add user</h4>
<div id='newuser'>
    <div id="newuser_form_container">
		<form id="add_member" class="wiki-form"  method="post" action="/admin_add_user">
            <ul>
                <li id="li_1" >
                    <label class="description" for="newusername">Username</label>
                    <div>
                        <input id="newusername" name="newusername" class="element text medium" type="text" maxlength="255" value=""/>
                    </div>
                </li>
                <li id="li_2" >
                    <label class="description" for="newpassword">Password</label>
                    <div>
                        <input id="newpassword" name="newpassword" class="element text medium" type="password" maxlength="255" value=""/>
                    </div>
                </li>
                <li id="li_3" >
                    <label class="description" for="confirmpassword">Confirm password</label>
                    <div>
                        <input id="confirmpassword" name="confirmpassword" class="element text medium" type="password" maxlength="255" value=""/>
                    </div>
                </li>
                <li class="buttons">
                        <input type="hidden" name="form_id" value="878252" />
                        <input id="saveForm" class="ncms_buttons" type="submit" name="submit" value="Add" />
                </li>
            </ul>
		</form>
	</div>
</div>

<h4 class='page-title'>Add wiki root category</h4>
<div id='wiki_cat'>
    <div id="wiki_cat_form_container">
		<form id="add_wiki_category" class="wiki-form" method="post" action="/wiki/add_category">
            <ul>
                <li >
                    <label class="description" for="category_name">Category name</label>
                    <div>
                        <input id="category_name" name="category_name" class="element text medium" type="text" maxlength="255" value=""/>
                    </div>
                </li>
                <li class="buttons">
                    <input type="hidden" name="form_id" value="568743" />
                    <input id="save_wiki_cat_form" class="ncms_buttons" type="submit" name="submit" value="Add" />
                </li>
            </ul>
		</form>
	</div>
</div>


