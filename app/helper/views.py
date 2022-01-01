
from flask.templating import render_template
from flask_login.utils import login_required, current_user
import pandas as pd
from werkzeug.utils import redirect
from flask.helpers import url_for

from app import helper, db
from app.models import Case, CaseStatus
from app.helper.forms import PCUCSVUplodForm
from app.helper import helper


@helper.route('/upload_pcu', methods=['GET', 'POST'])
@login_required
def upload_csv():
    form = PCUCSVUplodForm()

    if form.validate_on_submit():
        filestream = form.file.data
        # filename = secure_filename(filestream.filename)
        df = pd.read_csv( filestream )
        cases = []
        for index, row in df[:5].iterrows():
            # print(row['CP_NUM'], row['PartType'], row['Group'], row['Location'])
            new_case = Case(
                cp_num=row['CP_NUM'],
                specimen_class=row['SpecimenClass'],
                part_type=row['PartType'],
                group_external_value=row['Group'],
                part_description=row['PartDescription'],
                block_count=row['BlockCount'],
                doctor_code=row['DoctorCode'],
                specialty=row['Specialty'],
                location=row['Location'],
                PCU=0,
                status = CaseStatus.Created,
                assignee_id = current_user.id

            )
            cases.append(new_case)

        print(len(cases))
        db.session.add_all(cases)
        db.session.commit()

        return redirect(url_for('main.index'))
    
    return render_template('workflow/upload_csv.html', title='Upload CSV', form=form)