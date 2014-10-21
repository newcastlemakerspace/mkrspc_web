
% include('templates/mkrspc_front_header.tpl')

<h2 class='page-title'>Home</h2>

<div id='content'>

    <div id="osm-map" style="float:right; margin:5px;">
        <iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="http://www.openstreetmap.org/export/embed.html?bbox=151.74431204795837%2C-32.92711234001095%2C151.75965428352356%2C-32.91923227704827&amp;layer=mapnik&amp;marker=-32.92317239624756%2C151.75198316574097" style="border: 1px solid black"></iframe>
        <br/>
        <small>
        <a href="http://www.openstreetmap.org/?mlat=-32.9232&amp;mlon=151.7519#map=16/-32.9232/151.7519&amp;layers=N">View Larger Map</a>
        </small>
    </div>

    <p>Newcastle Makerspace is at 21 Gordon St, Hamilton, around the back, through the gate. View Map</p>

    <H3>Meeting times:</H3>

    <p>Every 1st, 3rd, and 5th Monday of the month, usually around 6pm.</p>

    <p>Every following Sunday of the month, usually around 10:30am.</p>

    <p>Organisation meetings at the first Sunday meeting of the month.</p>

    <p>The space is open irregularly at other times.</p>

    <br />
    <br />
    <br />
    <br />

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


