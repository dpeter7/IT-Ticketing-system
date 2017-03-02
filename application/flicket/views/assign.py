#! usr/bin/python3
# -*- coding: utf8 -*-

from flask import redirect, url_for, flash, g, render_template
from flask_login import login_required

from application import app, db
from application.flicket.forms.flicket_forms import SearchEmailForm
from application.flicket.models.flicket_models import FlicketTicket, FlicketStatus
from application.flicket.models.flicket_user import FlicketUser
from application.flicket.scripts.flicket_functions import announcer_post
from application.flicket.scripts.email import FlicketMail, get_recipients
from . import flicket_bp


# tickets main
@flicket_bp.route(app.config['FLICKET'] + 'ticket_assign/<int:ticket_id>/', methods=['GET', 'POST'])
@login_required
def ticket_assign(ticket_id=False):
    form = SearchEmailForm()
    ticket = FlicketTicket.query.filter_by(id=ticket_id).first()

    if ticket.current_status.status == 'Closed':
        flash("Can't assign a closed ticket.")
        return redirect(url_for('flicket_bp.ticket_view', ticket_id=ticket_id))

    if form.validate_on_submit():
        user = FlicketUser.query.filter_by(email=form.email.data).first()

        # assign ticket
        # set status to in work
        status = FlicketStatus.query.filter_by(status='In Work').first()
        ticket.assigned = user
        ticket.current_status = status
        db.session.commit()

        # add post to say user claimed ticket.
        announcer_post(ticket_id, g.user, 'Ticket assigned to {} by'.format(user.username))

        # send email to state ticket has been assigned.
        f_mail = FlicketMail()
        f_mail.assign_ticket(ticket)

        flash('You reassigned ticket:{}'.format(ticket.id))
        return redirect(url_for('flicket_bp.ticket_view', ticket_id=ticket.id))

    return render_template("flicket_assign.html", title="Assign Ticket", form=form, ticket=ticket)