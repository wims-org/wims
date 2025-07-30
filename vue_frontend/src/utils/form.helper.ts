import TextField from '@/components/fields/TextField.vue';
import TextAreaField from '@/components/fields/TextAreaField.vue';
import ObjectField from '@/components/fields/ObjectField.vue';
import LoadingField from '@/components/fields/LoadingField.vue';
import CheckboxField from '@/components/fields/CheckboxField.vue';
import ArrayField from '@/components/fields/ArrayField.vue';
import ModalField from '@/components/fields/ModalField.vue';
import NumberField from '@/components/fields/NumberField.vue';
import ImageThumbnailField from '@/components/fields/ImageThumbnailField.vue';
import ItemField from '@/components/fields/ItemField.vue';

export const fieldTypeToComponent = (type: string) => {
  const componentMap: Record<string, unknown> = {
    textarea: TextAreaField,
    object: ObjectField,
    loading: LoadingField,
    checkbox: CheckboxField,
    array: ArrayField,
    uuid: ModalField,
    number: NumberField,
    images: ImageThumbnailField,
    item: ItemField,

    text: TextField,
    imageThumbnail: ImageThumbnailField,
    image: ImageThumbnailField,
    file: ImageThumbnailField,
    default: TextField
  };
  return componentMap[type] || null;
}
