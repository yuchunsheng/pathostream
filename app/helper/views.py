
from flask.templating import render_template
from flask_login.utils import login_required, current_user
import pandas as pd
from werkzeug.utils import redirect
from flask.helpers import url_for

from app import helper, db
from app.models import Case, CaseStatus, PCU_Lookup
from app.helper.forms import PCUCSVUplodForm
from app.helper import helper


@helper.route('/upload_pcu', methods=['GET', 'POST'])
@login_required
def upload_pcu():
    form = PCUCSVUplodForm()

    if form.validate_on_submit():
        filestream = form.file.data
        # filename = secure_filename(filestream.filename)
        df = pd.read_csv( filestream )
        df = df.fillna('')
        pcu_lookups = []
        for index, row in df.iterrows():
            jk_pcu = row['New JK PCU']
            try:
                float(jk_pcu)
            except ValueError:
                jk_pcu=0.0
            
            new_PCU_Lookup = PCU_Lookup(
                part_type = row['PartType'],
                jk_type = row['JK Type'],
                new_jk_class = row['New JK Class'],
                new_jk_pcu= jk_pcu,
                comments = row['Comments']
            )
            
            pcu_lookups.append(new_PCU_Lookup)
            # print(row['PartType'], row['New JK PCU'], row['Comments'], row['JK Type'])

        print(len(pcu_lookups))
        db.session.add_all(pcu_lookups)
        db.session.commit()

        return redirect(url_for('helper.upload_pcu_done'))
    
    return render_template('helper/upload_pcu.html', title='Upload CSV', form=form)


@helper.route('/upload_pcu_done', methods=['GET', 'POST'])
@login_required
def upload_pcu_done():
    return render_template('helper/upload_pcu_done.html', title='Upload PCU done')