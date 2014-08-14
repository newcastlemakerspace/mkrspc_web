
% include('templates/mkrspc_front_header.tpl')

<h2 class='page-title'>Home</h2>

<div id='content'>
    <p>Our space is located at "Casablanca", 21 Gordon Avenue (Rear Building), Hamilton East, NSW</p><p><span style="line-height: 5px;">We are open for making on the first Sunday of the month at 10AM and the third Monday of the month at 6PM. </span><span style="line-height: 5px;">Organisational meetings are on the second Wednesday of the month at 6PM.</span></p>

</div>

%if show_login_form:
<h3 class='page-title'>Member login</h3>  <!-- todo need css for all this -->
<div id='login'>
    <p></p>
    <div id="form_container">
		<form id="member_login" class="loginform"  method="post" action="/login">
            <ul >
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
                <li class="buttons">
                        <input type="hidden" name="form_id" value="878252" />
                        <input id="saveForm" class="ncms_buttons" type="submit" name="submit" value="Sign in" />
                </li>
            </ul>
		</form>
	</div>
</div>
%end

% include('templates/mkrspc_front_footer.tpl')


