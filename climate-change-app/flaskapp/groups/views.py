"""
Contains view functions and routes for the groups section
"""

from uuid import UUID

from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.sql import insert

from flaskapp.extensions import db, over_16_required
from flaskapp.groups.forms import CreateGroupForm, EditGroupForm
from flaskapp.models.group import Group, association_table
from flaskapp.models.user import User

bp = Blueprint('groups', __name__, template_folder='templates')


# view groups homepage
@bp.route('/groups_dashboard/', defaults={'focus_group_id': None, 'mode': "my_groups"})
@bp.route('/groups_dashboard/<mode>', defaults={'focus_group_id': None})
@bp.route('/groups_dashboard/<mode>/<focus_group_id>', methods=['GET'])
@login_required
@over_16_required
def groups_dashboard(mode, focus_group_id):
    # get list of groups user is member of
    user_id = current_user.id
    users_groups = db.session.query(Group).join(Group.members).filter(User.id == user_id).all()
    # get list of all groups
    all_groups = db.session.query(Group).all()

    # set focussed group
    if focus_group_id:
        focus_group_id = UUID(focus_group_id)
        focussed_group = Group.query.filter_by(id=focus_group_id).first()
    else:
        focussed_group = None
    # get list of members/attendees if focussed group

    focussed_group_members = []
    if focussed_group:
        for member in focussed_group.get_members():
            focussed_group_members.append([member.username, focussed_group.is_attending(member)])
    else:
        focussed_group = 0

    return render_template('groups/groups_dashboard.html',
                           users_groups=users_groups,
                           all_groups=all_groups,
                           focussed_group=focussed_group,
                           focussed_group_members=focussed_group_members,
                           mode=mode)


# create group
@bp.route('/create_group', methods=['GET', 'POST'])
@login_required
@over_16_required
def create_group():
    # create CreateGroupForm object
    form = CreateGroupForm()

    # if request method is POST or form is valid
    if form.validate_on_submit():
        group = Group.query.filter_by(title=form.title.data).first()
        # if this returns a group, title is already in use

        # if title in use, redirect back to create group page
        if group:
            flash('A group with this title already exists.')
            return render_template('groups/create_group.html', form=form)

        # else create new group
        new_group = Group(title=form.title.data,
                          description=form.description.data,
                          location=form.location.data,
                          event_date=form.event_date.data,
                          owner=current_user.id)
        # add new group to database
        db.session.add(new_group)
        db.session.commit()

        # add owner as a member
        ins = insert(association_table).values(user_id=current_user.id, group_id=new_group.id, attending=True)
        db.session.execute(ins)
        db.session.commit()
        flash('Group successfully created!')
        return redirect(url_for('groups.groups_dashboard', mode="my_groups", focus_group_id=new_group.id))

    # if request method is GET, or group name invalid, rerender form
    return render_template('groups/create_group.html', form=form)


@bp.route('/edit_group/<group_id>', methods=['GET', 'POST'])
@login_required
@over_16_required
def edit_group(group_id):
    # create EditGroupForm object
    form = EditGroupForm()

    # convert group id to UUID
    group_id_uuid = UUID(group_id)

    # get group object
    group_editing = Group.query.filter_by(id=group_id_uuid).first()

    # if request method is POST, or form is valid
    if form.validate_on_submit():
        title_check = Group.query.filter(Group.title == form.title.data, Group.id != group_id_uuid).first()
        # if this returns a group that isn't current group, title already in use
        if title_check:
            flash('A group with this title already exists.')
            return render_template('groups/edit_group.html',
                                   group_id=group_id,
                                   form=form,
                                   group_editing=group_editing)

        # else update group
        group = Group.query.filter_by(id=group_id_uuid).first()
        if form.title.data != group.title and form.title.data != '':
            group.title = form.title.data
        if form.description.data != group.description and form.description.data != '':
            group.description = form.description.data
        if form.location.data != group.location and form.location.data != '':
            group.location = form.location.data
        if form.event_date.data != group.event_date and form.event_date.data is not None:
            group.event_date = form.event_date.data

        db.session.commit()
        flash("Group successfully edited!")
        return redirect(url_for('groups.groups_dashboard', mode="my_groups", focus_group_id=group.id))

    # if request method is GET, render form
    return render_template('groups/edit_group.html',
                           group_id=group_id,
                           form=form,
                           group_editing=group_editing)


@bp.route('/groups/delete_group/<group_id>', methods=['GET'])
@login_required
@over_16_required
def delete_group(group_id):
    # get group
    group_uuid = UUID(group_id)
    group = Group.query.filter_by(id=group_uuid).first()

    # check user is group owner
    if current_user.id == group.owner:
        db.session.delete(group)
        db.session.commit()
        flash('Group successfully deleted!')
        return redirect(url_for('groups.groups_dashboard'))

    return redirect(url_for('groups.groups_dashboard'))


@bp.route('/groups/leave_group/<group_id>', methods=['GET'])
@login_required
@over_16_required
def leave_group(group_id):
    # get group
    group_uuid = UUID(group_id)
    group = Group.query.filter_by(id=group_uuid).first()

    # check user is in group
    if group.is_member(current_user):
        group.remove_current_user()
        flash('Left group successfully!')
    return redirect(url_for('groups.groups_dashboard', mode="all_groups", focus_group_id=group_id))


@bp.route('/groups/join_group/<group_id>', methods=['GET'])
@login_required
@over_16_required
def join_group(group_id):
    # get group
    group_uuid = UUID(group_id)
    group = Group.query.filter_by(id=group_uuid).first()

    # check user isn't already in group
    if not group.is_member(current_user):
        group.add_current_user()
        flash('Joined group successfully!')
    return redirect(url_for('groups.groups_dashboard', mode="my_groups", focus_group_id=group_id))


@bp.route('/groups/attending/<group_id>', methods=['GET'])
@login_required
@over_16_required
def attending(group_id):
    # get group
    group_uuid = UUID(group_id)
    group = Group.query.filter_by(id=group_uuid).first()
    # get current attending status
    toggle_status = not group.is_attending(current_user)
    # remove current user from group
    group.remove_current_user()
    # add user back to group
    ins = insert(association_table).values(user_id=current_user.id, group_id=group.id, attending=toggle_status)
    db.session.execute(ins)
    db.session.commit()
    flash('Changed attending status successfully!')
    return redirect(url_for('groups.groups_dashboard', mode="my_groups", focus_group_id=group_id))
