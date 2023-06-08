
from django import forms
from django.utils.safestring import mark_safe


DEFAULT_PROFILE_IMAGE = '/static/blank.png' #'https://s3.amazonaws.com/spoonflower/public/design_thumbnails/0204/4896/solid_lt_grey_B5B5B5_shop_thumb.png'


class ImagePreviewWidget(forms.widgets.FileInput):
    def __init__(self, label='', *args, **kwargs):
        self.label = label
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None, **kwargs):
        input_html = super().render(name, value,
                                    attrs={'class':'form-control',
                                            'placeholder': 'upload photo image (jpg, gif)'},
                                    **kwargs)
        if value is None:
            if self.attrs.get('old_value'):
                value = self.attrs['old_value']
            else:
                image_path = DEFAULT_PROFILE_IMAGE
        else:
            try:
                image_path = str(value)  # Convert the value to a string
                if image_path.startswith('media/'):
                    image_path = image_path[len('media/'):]  # Remove the 'media/' prefix
            except Exception as e:
                image_path = value

        img_html = mark_safe(f'<img src="{image_path}" width="50" height="50" class="avatar64" />')

        return f'''<div class="row">
                    <div class="col-2" align="center">
                        {img_html}
                    </div>
                    <div class="col-10">
                        {self.label}
                        {input_html}
                    </div>'''
