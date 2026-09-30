<script setup lang="ts">
import StarterKit from '@tiptap/starter-kit'
import { EditorContent, useEditor } from '@tiptap/vue-3'

const model = defineModel<string>({ default: '' })
const editor = useEditor({
  content: model.value,
  extensions: [StarterKit],
  onUpdate: ({ editor: current }) => {
    model.value = current.getHTML()
  },
})
</script>

<template>
  <div class="admin-field">
    <span>Aviso de privacidad</span>
    <EditorContent v-if="editor" :editor="editor" />
  </div>
</template>
