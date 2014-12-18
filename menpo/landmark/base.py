import abc
from collections import OrderedDict, MutableMapping

import numpy as np

from menpo.base import Copyable
from menpo.transform.base import Transformable
from menpo.visualize import LandmarkViewer
from menpo.visualize.base import Viewable


class Landmarkable(Copyable):
    r"""
    Abstract interface for object that can have landmarks attached to them.
    Landmarkable objects have a public dictionary of landmarks which are
    managed by a :map:`LandmarkManager`. This means that
    different sets of landmarks can be attached to the same object.
    Landmarks can be N-dimensional and are expected to be some
    subclass of :map:`PointCloud`. These landmarks
    are wrapped inside a :map:`LandmarkGroup` object that performs
    useful tasks like label filtering and viewing.
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._landmarks = None

    @abc.abstractproperty
    def n_dims(self):
        pass

    @property
    def landmarks(self):
        if self._landmarks is None:
            self._landmarks = LandmarkManager()
        return self._landmarks

    @property
    def has_landmarks(self):
        return self._landmarks is not None

    @landmarks.setter
    def landmarks(self, value):
        # firstly, make sure the dim is correct. Note that the dim can be None
        lm_n_dims = value.n_dims
        if lm_n_dims is not None and lm_n_dims != self.n_dims:
            raise ValueError(
                "Trying to set {}D landmarks on a "
                "{}D object".format(value.n_dims, self.n_dims))
        self._landmarks = value.copy()

    @property
    def n_landmark_groups(self):
        r"""
        The number of landmark groups on this object.

        :type: `int`
        """
        return self.landmarks.n_groups


class LandmarkableViewable(Landmarkable, Viewable):
    r"""
    Mixin for :map:`Landmarkable` and :map:`Viewable` objects. Provides a
    single helper method for viewing Landmarks and slf on the same figure.
    """

    def view_landmarks(self, channels=None, masked=True, group=None,
                       with_labels=None, without_labels=None,
                       figure_id=None, new_figure=False, render_lines=True,
                       line_colour='r', line_style='-', line_width=1,
                       render_markers=True, marker_style='o', marker_size=20,
                       marker_face_colour='k', marker_edge_colour='k',
                       marker_edge_width=1., render_numbering=False,
                       numbers_horizontal_align='center',
                       numbers_vertical_align='bottom',
                       numbers_font_name='sans-serif', numbers_font_size=10,
                       numbers_font_style='normal',
                       numbers_font_weight='normal', numbers_font_colour='k',
                       render_legend=True, legend_title='',
                       legend_font_name='sans-serif',
                       legend_font_style='normal', legend_font_size=10,
                       legend_font_weight='normal', legend_marker_scale=None,
                       legend_location=2, legend_bbox_to_anchor=(1.05, 1.),
                       legend_border_axes_pad=None, legend_n_columns=1,
                       legend_horizontal_spacing=None,
                       legend_vertical_spacing=None, legend_border=True,
                       legend_border_padding=None, legend_shadow=False,
                       legend_rounded_corners=False, render_axes=True,
                       axes_font_name='sans-serif', axes_font_size=10,
                       axes_font_style='normal', axes_font_weight='normal',
                       axes_x_limits=None, axes_y_limits=None,
                       figure_size=(6, 4)):
        """
        View all landmarks on the current shape, using the default
        shape view method. Kwargs passed in here will be passed through
        to the shapes view method.

        Parameters
        ----------
        group : `str`, optional
            If ``None``, show all groups, else show only the provided group.
        render_numbering : `bool`, optional
            If ``True``, also render the label names next to the landmarks.
        render_legend : `bool`, optional
            If ``True``, also render a legend showing the landmark group symbols
            and colours.
        with_labels : ``None`` or `str` or `list` of `str`, optional
            If not ``None``, only show the given label(s). Should **not** be
            used with the ``without_labels`` kwarg.
        without_labels : ``None`` or `str` or `list` of `str`, optional
            If not ``None``, show all except the given label(s). Should **not**
            be used with the ``with_labels`` kwarg.
        lmark_view_kwargs : `dict`, optional
            Passed through to the landmark viewer. An example for 3 labels:
                lmark_view_kwargs = {'labels_colours': ['r', 'g', 'b'],
                                     'marker_sizes': 20,
                                     'marker_styles': 'o',
                                     'edge_colours': 'k',
                                     'face_colours': 'b',
                                     'line_styles': 'solid',
                                     'line_widths': 1,
                                     'halign': 'center',
                                     'valign': 'bottom',
                                     'font_size': 10}
        obj_view_kwargs : `dict`, optional
            Passed through to this object's viewer.

        Raises
        ------
        ValueError
            If both ``with_labels`` and ``without_labels`` are passed.
        ValueError
            If the landmark manager doesn't contain the provided group label.
        """
        import matplotlib.pyplot as plt

        # Render self
        from menpo.image import MaskedImage
        if isinstance(self, MaskedImage):
            self_view = self.view(figure_id=figure_id, new_figure=new_figure,
                                  channels=channels, masked=masked)
        else:
            self_view = self.view(figure_id=figure_id, new_figure=new_figure,
                                  channels=channels)

        # Make sure axes are constrained to the image size
        if axes_x_limits is None:
            axes_x_limits = [0, self.width - 1]
        if axes_y_limits is None:
            axes_y_limits = [0, self.height - 1]

        # Render landmarks
        landmark_view = None  # initialize viewer object
        axes_list = plt.gcf().get_axes()  # get axis objects
        # useful in order to visualize the legend only for the last axis object
        render_legend_tmp = False
        for i, ax in enumerate(axes_list):
            # set current axis
            plt.sca(ax)

            # show legend only for the last axis object
            if i == len(axes_list) - 1:
                render_legend_tmp = render_legend

            # viewer
            landmark_view = self.landmarks.view(
                with_labels=with_labels, without_labels=without_labels,
                group=group, figure_id=self_view.figure_id, new_figure=False,
                image_view=True, render_lines=render_lines,
                line_colour=line_colour, line_style=line_style,
                line_width=line_width, render_markers=render_markers,
                marker_style=marker_style, marker_size=marker_size,
                marker_face_colour=marker_face_colour,
                marker_edge_colour=marker_edge_colour,
                marker_edge_width=marker_edge_width,
                render_numbering=render_numbering,
                numbers_horizontal_align=numbers_horizontal_align,
                numbers_vertical_align=numbers_vertical_align,
                numbers_font_name=numbers_font_name,
                numbers_font_size=numbers_font_size,
                numbers_font_style=numbers_font_style,
                numbers_font_weight=numbers_font_weight,
                numbers_font_colour=numbers_font_colour,
                render_legend=render_legend_tmp, legend_title=legend_title,
                legend_font_name=legend_font_name,
                legend_font_style=legend_font_style,
                legend_font_size=legend_font_size,
                legend_font_weight=legend_font_weight,
                legend_marker_scale=legend_marker_scale,
                legend_location=legend_location,
                legend_bbox_to_anchor=legend_bbox_to_anchor,
                legend_border_axes_pad=legend_border_axes_pad,
                legend_n_columns=legend_n_columns,
                legend_horizontal_spacing=legend_horizontal_spacing,
                legend_vertical_spacing=legend_vertical_spacing,
                legend_border=legend_border,
                legend_border_padding=legend_border_padding,
                legend_shadow=legend_shadow,
                legend_rounded_corners=legend_rounded_corners,
                render_axes=render_axes, axes_font_name=axes_font_name,
                axes_font_size=axes_font_size, axes_font_style=axes_font_style,
                axes_font_weight=axes_font_weight, axes_x_limits=axes_x_limits,
                axes_y_limits=axes_y_limits, figure_size=figure_size)

        return landmark_view


class LandmarkManager(MutableMapping, Transformable, Viewable):
    """
    Class for storing and manipulating Landmarks associated with an object.
    This involves managing the internal dictionary, as well as providing
    convenience functions for operations like viewing.

    A LandmarkManager ensures that all it's Landmarks are of the
    same dimensionality.

    """
    def __init__(self):
        super(LandmarkManager, self).__init__()
        self._landmark_groups = {}

    @property
    def n_dims(self):
        if self.n_groups != 0:
            # Python version independent way of getting the first value
            for v in self._landmark_groups.values():
                return v.n_dims
        else:
            return None

    def copy(self):
        r"""
        Generate an efficient copy of this :map:`LandmarkManager`.

        Returns
        -------

        ``type(self)``
            A copy of this object

        """
        # do a normal copy. The dict will be shallow copied - rectify that here
        new = Copyable.copy(self)
        for k, v in new._landmark_groups.items():
            new._landmark_groups[k] = v.copy()
        return new

    def __iter__(self):
        """
        Iterate over the internal landmark group dictionary
        """
        return iter(self._landmark_groups)

    def __setitem__(self, group, value):
        """
        Sets a new landmark group for the given label. This can be set using
        an existing landmark group, or using a PointCloud. Existing landmark
        groups will have their target reset. If a PointCloud is provided then
        all landmarks belong to a single label `all`.

        Parameters
        ----------
        group : `string`
            Label of new group.

        value : :map:`LandmarkGroup` or :map:`PointCloud`
            The new landmark group to set.

        Raises
        ------
        DimensionalityError
            If the landmarks and the shape are not of the same dimensionality.
        """
        from menpo.shape import PointCloud
        # firstly, make sure the dim is correct
        n_dims = self.n_dims
        if n_dims is not None and value.n_dims != n_dims:
            raise ValueError(
                "Trying to set {}D landmarks on a "
                "{}D LandmarkManager".format(value.n_dims, self.n_dims))
        if isinstance(value, PointCloud):
            # Copy the PointCloud so that we take ownership of the memory
            lmark_group = LandmarkGroup(
                value,
                OrderedDict([('all', np.ones(value.n_points, dtype=np.bool))]))
        elif isinstance(value, LandmarkGroup):
            # Copy the landmark group so that we now own it
            lmark_group = value.copy()
            # check the target is set correctly
            lmark_group._group_label = group
        else:
            raise ValueError('Valid types are PointCloud or LandmarkGroup')

        self._landmark_groups[group] = lmark_group

    def __getitem__(self, group=None):
        """
        Returns the group for the provided label.

        Parameters
        ---------
        group : `string`, optional
            The label of the group. If None is provided, and if there is only
            one group, the unambiguous group will be returned.
        Returns
        -------
        lmark_group : :map:`LandmarkGroup`
            The matching landmark group.
        """
        if group is None:
            if self.n_groups == 1:
                group = self.group_labels[0]
            else:
                raise ValueError("Cannot use None as a key as there are {} "
                                 "landmark groups".format(self.n_groups))
        return self._landmark_groups[group]

    def __delitem__(self, group):
        """
        Delete the group for the provided label.

        Parameters
        ---------
        group : `string`
            The label of the group.
        """
        del self._landmark_groups[group]

    def __len__(self):
        return len(self._landmark_groups)

    @property
    def n_groups(self):
        """
        Total number of labels.

        :type: `int`
        """
        return len(self._landmark_groups)

    @property
    def has_landmarks(self):
        """
        Whether the object has landmarks or not

        :type: `int`
        """
        return self.n_groups != 0

    @property
    def group_labels(self):
        """
        All the labels for the landmark set.

        :type: list of `string`
        """
        return self._landmark_groups.keys()

    def _transform_inplace(self, transform):
        for group in self._landmark_groups.values():
            group.lms._transform_inplace(transform)
        return self

    def view(self, group=None, with_labels=None, without_labels=None,
             figure_id=None, new_figure=False, image_view=False,
             render_lines=True, line_colour='r', line_style='-', line_width=1,
             render_markers=True, marker_style='o', marker_size=20,
             marker_face_colour='k', marker_edge_colour='k',
             marker_edge_width=1., render_numbering=False,
             numbers_horizontal_align='center', numbers_vertical_align='bottom',
             numbers_font_name='sans-serif', numbers_font_size=10,
             numbers_font_style='normal', numbers_font_weight='normal',
             numbers_font_colour='k', render_legend=True, legend_title='',
             legend_font_name='sans-serif', legend_font_style='normal',
             legend_font_size=10, legend_font_weight='normal',
             legend_marker_scale=None, legend_location=2,
             legend_bbox_to_anchor=(1.05, 1.), legend_border_axes_pad=None,
             legend_n_columns=1, legend_horizontal_spacing=None,
             legend_vertical_spacing=None, legend_border=True,
             legend_border_padding=None, legend_shadow=False,
             legend_rounded_corners=False, render_axes=True,
             axes_font_name='sans-serif', axes_font_size=10,
             axes_font_style='normal', axes_font_weight='normal',
             axes_x_limits=None, axes_y_limits=None, figure_size=(6, 4)):
        """
        View all landmarks groups on the current manager.

        Parameters
        ----------
        group : `str`, optional
            If ``None``, show all groups, else show only the provided group.
        render_numbering : `boolean`, optional
            If ``True``, also render the label names next to the landmarks.
        render_legend : `bool`, optional
            If ``True``, also render the legend.
        with_labels : None or `str` or list of `str`, optional
            If not ``None``, only show the given label(s). Should **not** be
            used with the ``without_labels`` kwarg.
        without_labels : None or `str` or list of `str`, optional
            If not ``None``, show all except the given label(s). Should **not**
            be used with the ``with_labels`` kwarg.
        kwargs : `dict`, optional
            Passed through to the viewer.

        Raises
        ------
        ValueError
            If both ``with_labels`` and ``without_labels`` are passed.
        ValueError
            If the landmark manager doesn't contain the provided group label.
        """
        # Check that the provided group belongs to the groups dict or is None
        # and there's only one group available
        if group is None:
            if self.n_groups == 1:
                g_label = self._landmark_groups.keys()[0]
            else:
                raise ValueError('A group must be specified as there are '
                                 '{} groups in total.'.format(self.n_groups))
        elif group in self._landmark_groups:
            g_label = group
        else:
            raise ValueError('Unknown group {}'.format(group))

        # Render
        return self._landmark_groups[g_label].view(
            with_labels=with_labels, without_labels=without_labels,
            group=g_label, figure_id=figure_id, new_figure=new_figure,
            image_view=image_view, render_lines=render_lines,
            line_colour=line_colour, line_style=line_style,
            line_width=line_width, render_markers=render_markers,
            marker_style=marker_style, marker_size=marker_size,
            marker_face_colour=marker_face_colour,
            marker_edge_colour=marker_edge_colour,
            marker_edge_width=marker_edge_width,
            render_numbering=render_numbering,
            numbers_horizontal_align=numbers_horizontal_align,
            numbers_vertical_align=numbers_vertical_align,
            numbers_font_name=numbers_font_name,
            numbers_font_size=numbers_font_size,
            numbers_font_style=numbers_font_style,
            numbers_font_weight=numbers_font_weight,
            numbers_font_colour=numbers_font_colour,
            render_legend=render_legend, legend_title=legend_title,
            legend_font_name=legend_font_name,
            legend_font_style=legend_font_style,
            legend_font_size=legend_font_size,
            legend_font_weight=legend_font_weight,
            legend_marker_scale=legend_marker_scale,
            legend_location=legend_location,
            legend_bbox_to_anchor=legend_bbox_to_anchor,
            legend_border_axes_pad=legend_border_axes_pad,
            legend_n_columns=legend_n_columns,
            legend_horizontal_spacing=legend_horizontal_spacing,
            legend_vertical_spacing=legend_vertical_spacing,
            legend_border=legend_border,
            legend_border_padding=legend_border_padding,
            legend_shadow=legend_shadow,
            legend_rounded_corners=legend_rounded_corners,
            render_axes=render_axes, axes_font_name=axes_font_name,
            axes_font_size=axes_font_size, axes_font_style=axes_font_style,
            axes_font_weight=axes_font_weight, axes_x_limits=axes_x_limits,
            axes_y_limits=axes_y_limits, figure_size=figure_size)

    def view_widget(self, popup=False):
        r"""
        Visualizes the landmark manager object using the
        menpo.visualize.widgets.visualize_shapes widget.

        Parameters
        -----------
        popup : `boolean`, optional
            If enabled, the widget will appear as a popup window.
        """
        from menpo.visualize import visualize_shapes
        visualize_shapes(self, figure_size=(7, 7), popup=popup)

    def __str__(self):
        out_string = '{}: n_groups: {}'.format(type(self).__name__,
                                               self.n_groups)
        if self.has_landmarks:
            for label in self:
                out_string += '\n'
                out_string += '({}): {}'.format(label, self[label].__str__())

        return out_string


class LandmarkGroup(MutableMapping, Copyable, Viewable):
    """
    An immutable object that holds a :map:`PointCloud` (or a subclass) and
    stores labels for each point. These labels are defined via masks on the
    :map:`PointCloud`. For this reason, the :map:`PointCloud` is considered to
    be immutable.

    The labels to masks must be within an `OrderedDict` so that semantic
    ordering can be maintained.

    Parameters
    ----------
    target : :map:`Landmarkable`
        The parent object of this landmark group.
    group : `string`
        The label of the group.
    pointcloud : :map:`PointCloud`
        The pointcloud representing the landmarks.
    labels_to_masks : `OrderedDict` of `string` to `boolean` `ndarrays`
        For each label, the mask that specifies the indices in to the
        pointcloud that belong to the label.
    copy : `boolean`, optional
        If ``True``, a copy of the :map:`PointCloud` is stored on the group.

    Raises
    ------
    ValueError
        If `dict` passed instead of `OrderedDict`
    ValueError
        If no set of label masks is passed.
    ValueError
        If any of the label masks differs in size to the pointcloud.
    ValueError
        If there exists any point in the pointcloud that is not covered
        by a label.
    """

    def __init__(self, pointcloud, labels_to_masks, copy=True):
        super(LandmarkGroup, self).__init__()

        if not labels_to_masks:
            raise ValueError('Landmark groups are designed for their internal '
                             'state, other than owernship, to be immutable. '
                             'Empty label sets are not permitted.')
        if np.vstack(labels_to_masks.values()).shape[1] != pointcloud.n_points:
            raise ValueError('Each mask must have the same number of points '
                             'as the landmark pointcloud.')
        if type(labels_to_masks) is dict:
            raise ValueError('Must provide an OrderedDict to maintain the '
                             'semantic meaning of the labels.')

        # Another sanity check
        self._labels_to_masks = labels_to_masks
        self._verify_all_labels_masked()

        if copy:
            self._pointcloud = pointcloud.copy()
            self._labels_to_masks = OrderedDict([(l, m.copy()) for l, m in
                                                 labels_to_masks.items()])
        else:
            self._pointcloud = pointcloud
            self._labels_to_masks = labels_to_masks

    def copy(self):
        r"""
        Generate an efficient copy of this :map:`LandmarkGroup`.

        Returns
        -------

        ``type(self)``
            A copy of this object

        """
        new = Copyable.copy(self)
        for k, v in new._labels_to_masks.items():
            new._labels_to_masks[k] = v.copy()
        return new

    def __iter__(self):
        """
        Iterate over the internal label dictionary
        """
        return iter(self._labels_to_masks)

    def __setitem__(self, label, indices):
        """
        Add a new label to the landmark group by adding a new set of indices

        Parameters
        ----------
        label : `string`
            Label of landmark.

        indices : ``(K,)`` `ndarray`
            Array of indices in to the pointcloud. Each index implies
            membership to the label.
        """
        mask = np.zeros(self._pointcloud.n_points, dtype=np.bool)
        mask[indices] = True
        self._labels_to_masks[label] = mask

    def __getitem__(self, label=None):
        """
        Returns the PointCloud that contains this label represents on the group.
        This will be a subset of the total landmark group PointCloud.

        Parameters
        ----------
        label : `string`
            Label to filter on.

        Returns
        -------
        pcloud : :map:`PointCloud`
            The PointCloud that this label represents. Will be a subset of the
            entire group's landmarks.
        """
        if label is None:
            return self.lms.copy()
        return self._pointcloud.from_mask(self._labels_to_masks[label])

    def __delitem__(self, label):
        """
        Delete the semantic labelling for the provided label.

         .. note::

             You cannot delete a semantic label and leave the landmark group
             partially unlabelled. Landmark groups must contain labels for
             every point.

        Parameters
        ---------
        label : `string`
            The label to remove.

        Raises
        ------
        ValueError
            If deleting the label would leave some points unlabelled
        """
        # Pop the value off, which is akin to deleting it (removes it from the
        # underlying dict). However, we keep it around so we can check if
        # removing it causes an unlabelled point
        value_to_delete = self._labels_to_masks.pop(label)

        try:
            self._verify_all_labels_masked()
        except ValueError as e:
            # Catch the error, restore the value and re-raise the exception!
            self._labels_to_masks[label] = value_to_delete
            raise e

    def __len__(self):
        return len(self._labels_to_masks)

    @property
    def labels(self):
        """
        The list of labels that belong to this group.

        :type: list of `string`
        """
        return self._labels_to_masks.keys()

    @property
    def n_labels(self):
        """
        Number of labels in the group.

        :type: `int`
        """
        return len(self.labels)

    @property
    def lms(self):
        """
        The pointcloud representing all the landmarks in the group.

        :type: :map:`PointCloud`
        """
        return self._pointcloud

    @property
    def n_landmarks(self):
        """
        The total number of landmarks in the group.

        :type: `int`
        """
        return self._pointcloud.n_points

    @property
    def n_dims(self):
        """
        The dimensionality of these landmarks.

        :type: `int`
        """
        return self._pointcloud.n_dims

    def with_labels(self, labels=None):
        """
        Returns a new landmark group that contains only the given labels.

        Parameters
        ----------
        labels : `string` or list of `string`, optional
            Labels that should be kept in the returned landmark group. If
            None is passed, and if there is only one label on this group,
            the label will be substituted automatically.

        Returns
        -------
        landmark_group : :map:`LandmarkGroup`
            A new landmark group with the same group label but containing only
            the given label.
        """
        # make it easier by allowing None when there is only one label
        if labels is None:
            if self.n_labels == 1:
                labels = self.labels
            else:
                raise ValueError("Cannot use None as there are "
                                 "{} labels".format(self.n_labels))
        # Make it easier to use by accepting a single string as well as a list
        if isinstance(labels, str):
            labels = [labels]
        return self._new_group_with_only_labels(labels)

    def without_labels(self, labels):
        """
        Returns a new landmark group that contains all labels EXCEPT the given
        label.

        Parameters
        ----------
        label : `string`
            Label to exclude.

        Returns
        -------
        landmark_group : :map:`LandmarkGroup`
            A new landmark group with the same group label but containing all
            labels except the given label.
        """
        # Make it easier to use by accepting a single string as well as a list
        if isinstance(labels, str):
            labels = [labels]
        labels_to_keep = list(set(self.labels).difference(labels))
        return self._new_group_with_only_labels(labels_to_keep)

    def _verify_all_labels_masked(self):
        """
        Verify that every point in the pointcloud is associated with a label.
        If any one point is not covered by a label, then raise a
        ``ValueError``.
        """
        unlabelled_points = np.sum(self._labels_to_masks.values(), axis=0) == 0
        if np.any(unlabelled_points):
            raise ValueError('Every point in the landmark pointcloud must be '
                             'labelled. Points {0} were unlabelled.'.format(
                np.nonzero(unlabelled_points)))

    def _new_group_with_only_labels(self, labels):
        """
        Deal with changing indices when you add and remove points. In this case
        we only deal with building a new dataset that keeps masks.

        Parameters
        ----------
        labels : list of `string`
            List of strings of the labels to keep

        Returns
        -------
        lmark_group : :map:`LandmarkGroup`
            The new landmark group with only the requested labels.
        """
        set_difference = set(labels).difference(self.labels)
        if len(set_difference) > 0:
            raise ValueError('Labels {0} do not exist in the landmark '
                             'group. Available labels are: {1}'.format(
                list(set_difference), self.labels))

        masks_to_keep = [self._labels_to_masks[l] for l in labels
                         if l in self._labels_to_masks]
        overlap = np.sum(masks_to_keep, axis=0) > 0
        masks_to_keep = [l[overlap] for l in masks_to_keep]

        return LandmarkGroup(self._pointcloud.from_mask(overlap),
                             OrderedDict(zip(labels, masks_to_keep)))

    def tojson(self):
        r"""
        Convert this `LandmarkGroup` to a dictionary JSON representation.

        Returns
        -------
        Dictionary with 'groups' key. Groups contains a landmark label set,
        containing the label, spatial points and connectivity information.
        Suitable or use in the by the `json` standard library package.
        """
        from menpo.shape import TriMesh, PointUndirectedGraph

        groups = []
        for label in self:
            pcloud = self[label]
            if isinstance(pcloud, TriMesh):
                connectivity = [t.tolist()
                                for t in pcloud.as_pointgraph().adjacency_array]
            elif isinstance(pcloud, PointUndirectedGraph):
                connectivity = [t.tolist()
                                for t in pcloud.adjacency_array]
            else:
                connectivity = []
            landmarks = [{'point': p.tolist()} for p in pcloud.points]
            groups.append({'connectivity': connectivity,
                           'label': label,
                           'landmarks': landmarks})
        return {'groups': groups}

    def view(self, with_labels=None, without_labels=None, group='group',
             figure_id=None, new_figure=False, image_view=True,
             render_lines=True, line_colour=None, line_style='-', line_width=1,
             render_markers=True, marker_style='o', marker_size=20,
             marker_face_colour='r', marker_edge_colour='k',
             marker_edge_width=1., render_numbering=False,
             numbers_horizontal_align='center', numbers_vertical_align='bottom',
             numbers_font_name='sans-serif', numbers_font_size=10,
             numbers_font_style='normal', numbers_font_weight='normal',
             numbers_font_colour='k', render_legend=True, legend_title='',
             legend_font_name='sans-serif', legend_font_style='normal',
             legend_font_size=10, legend_font_weight='normal',
             legend_marker_scale=None, legend_location=2,
             legend_bbox_to_anchor=(1.05, 1.), legend_border_axes_pad=None,
             legend_n_columns=1, legend_horizontal_spacing=None,
             legend_vertical_spacing=None, legend_border=True,
             legend_border_padding=None, legend_shadow=False,
             legend_rounded_corners=False, render_axes=True,
             axes_font_name='sans-serif', axes_font_size=10,
             axes_font_style='normal', axes_font_weight='normal',
             axes_x_limits=None, axes_y_limits=None, figure_size=None):
        """
        View all landmarks.

        Parameters
        ----------
        targettype : `type`, optional
            Hint for the landmark viewer for the type of the object these
            landmarks are attached to. If ``None``, The landmarks will be
            visualized without special consideration for the type of the
            target. Mainly used for :map:`Image` subclasses.
        render_numbering : `bool`, optional
            If `True`, also render the label numbers next to the landmarks.
        render_legend : `bool`, optional
            If ``True``, also render the legend.
        group : `str`, optional
            The group label to prepend before the semantic labels
        with_labels : None or `str` or list of `str`, optional
            If not ``None``, only show the given label(s). Should **not** be
            used with the ``without_labels`` kwarg.
        without_labels : None or `str` or list of `str`, optional
            If not ``None``, show all except the given label(s). Should **not**
            be used with the ``with_labels`` kwarg.
        kwargs : `dict`, optional
            Passed through to the viewer.

        Raises
        ------
        ValueError
            If both ``with_labels`` and ``without_labels`` are passed.
        """
        if with_labels is not None and without_labels is not None:
            raise ValueError('You may only pass one of `with_labels` or '
                             '`without_labels`.')
        elif with_labels is not None:
            lmark_group = self.with_labels(with_labels)
        elif without_labels is not None:
            lmark_group = self.without_labels(without_labels)
        else:
            lmark_group = self  # Fall through
        landmark_viewer = LandmarkViewer(figure_id, new_figure, group,
                                         lmark_group._pointcloud,
                                         lmark_group._labels_to_masks)
        return landmark_viewer.render(
            image_view=image_view, render_lines=render_lines,
            line_colour=line_colour, line_style=line_style,
            line_width=line_width, render_markers=render_markers,
            marker_style=marker_style, marker_size=marker_size,
            marker_face_colour=marker_face_colour,
            marker_edge_colour=marker_edge_colour,
            marker_edge_width=marker_edge_width,
            render_numbering=render_numbering,
            numbers_horizontal_align=numbers_horizontal_align,
            numbers_vertical_align=numbers_vertical_align,
            numbers_font_name=numbers_font_name,
            numbers_font_size=numbers_font_size,
            numbers_font_style=numbers_font_style,
            numbers_font_weight=numbers_font_weight,
            numbers_font_colour=numbers_font_colour,
            render_legend=render_legend, legend_title=legend_title,
            legend_font_name=legend_font_name,
            legend_font_style=legend_font_style,
            legend_font_size=legend_font_size,
            legend_font_weight=legend_font_weight,
            legend_marker_scale=legend_marker_scale,
            legend_location=legend_location,
            legend_bbox_to_anchor=legend_bbox_to_anchor,
            legend_border_axes_pad=legend_border_axes_pad,
            legend_n_columns=legend_n_columns,
            legend_horizontal_spacing=legend_horizontal_spacing,
            legend_vertical_spacing=legend_vertical_spacing,
            legend_border=legend_border,
            legend_border_padding=legend_border_padding,
            legend_shadow=legend_shadow,
            legend_rounded_corners=legend_rounded_corners,
            render_axes=render_axes, axes_font_name=axes_font_name,
            axes_font_size=axes_font_size, axes_font_style=axes_font_style,
            axes_font_weight=axes_font_weight, axes_x_limits=axes_x_limits,
            axes_y_limits=axes_y_limits, figure_size=figure_size)

    def __str__(self):
        return '{}: n_labels: {}, n_points: {}'.format(
            type(self).__name__, self.n_labels, self.n_landmarks)
