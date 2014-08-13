% include('templates/mkrspc_wiki_header.tpl')

{{!main_content}}

%if editable == True:
<h4 class='page-title'>Add wiki article</h4>  <!-- todo need css for all this -->
<div id='wiki_subcat'>
    <p>Article will be created in category / subcategory.</p>
    <div id="wiki_article_form_container">
        <form id="wiki_controls" class="wikiform"  method="post" action="/wiki/new_article">
            <input type="hidden" name="form_id" value="6846541" />
            <input type="hidden" name="article_subcat_id" value="{{subcategory_id}}"/>
            <ul>
                <li>
                    <label class="description" for="article_title">Article title</label>
                    <div>
                        <input id="article_title" name="article_title" class="element text medium" type="text" maxlength="255" value=""/>
                    </div>
                </li>
                <li >
                    <label class="description" for="article_slug">Slug - (use CamelCase with no spaces, e.g. ArticleTitle)</label>
                    <div>
                        <input id="article_slug" name="article_slug" class="element text medium" type="text" maxlength="255" value=""/>
                    </div>

                </li>
            </ul>
            <input id="new_article" class="ncms_buttons" type="submit" name="submit" value="Create" />
            <input id="cancel_wiki" class="ncms_buttons" type="submit" name="submit" value="Cancel" />
        </form>
    </div>
</div>

%end

% include('templates/mkrspc_wiki_footer.tpl')
