% include('templates/mkrspc_front_header.tpl')
<h2 class='page-title'>Site Administration</h2>
<div id='content'>
    <p>Hi there, superuser.</p>
</div>

<h4 class='page-title'>Add user</h4>  <!-- todo need css for all this -->
<div id='login'>
    <p></p>
    <div id="newuser_form_container">
		<form id="add_member" class="loginform"  method="post" action="/admin_add_user">
            <ul>
                <li id="li_1" >
                    <label class="description" for="username">Username</label>
                    <div>
                        <input id="username" name="username" class="element text medium" type="text" maxlength="255" value=""/>
                    </div>
                </li>
                <li id="li_2" >
                    <label class="description" for="password">Password</label>
                    <div>
                        <input id="password" name="password" class="element text medium" type="password" maxlength="255" value=""/>
                    </div>
                </li>
                <li id="li_3" >
                    <label class="description" for="confirm_password">Confirm password</label>
                    <div>
                        <input id="confirm_password" name="confirm_password" class="element text medium" type="password" maxlength="255" value=""/>
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

<h4 class='page-title'>Add wiki article category</h4>  <!-- todo need css for all this -->
<div id='wiki_cat'>
    <p></p>
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

<h4 class='page-title'>Add wiki article sub-category</h4>  <!-- todo need css for all this -->
<div id='wiki_subcat'>
    <p></p>
    <div id="wiki_subcat_form_container">
		<form id="add_wiki_subcategory" class="wiki-form"  method="post" action="/wiki/add_subcategory">
            <ul>

                <li >
                    <label class="description" for="username">Category</label>
                    <div>
                        <select id="main_category" name="main_category" >
                          %if wiki_categories is not None:
                            %for cat in wiki_categories:
                              <option value="{{cat[0]}}">{{cat[1]}}</option>
                          %end
                        </select>
                    </div>
                </li>
                <li >
                    <label class="description" for="subcategory_name">Subcategory name</label>
                    <div>
                        <input id="subcategory_name" name="subcategory_name" class="element text medium" type="text" maxlength="255" value=""/>
                    </div>
                </li>
                <li class="buttons">
                    <input type="hidden" name="form_id" value="568743" />
                    <input id="save_wiki_subcat_form" class="ncms_buttons" type="submit" name="submit" value="Add" />
                </li>
            </ul>
		</form>
	</div>
</div>



% include('templates/mkrspc_front_footer.tpl')