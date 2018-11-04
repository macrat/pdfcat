<style scoped>
#app {
	height: 100vh;
}

.page {
	margin: 16px;
	display: inline-block;
}

input {
	display: none;
}
</style>

<template>
	<md-app id=app md-waterfall md-mode=fixed>
		<md-app-toolbar>
			<span class=md-title>PDFCat</span>
			<div class=md-toolbar-section-end>
				<md-button class=md-icon-button disabled><md-icon>undo</md-icon></md-button>
				<md-button class=md-icon-button disabled><md-icon>redo</md-icon></md-button>
				<md-button @click=save>save</md-button>
				<md-button class=md-icon-button disabled><md-icon>menu</md-icon></md-button>
			</div>
		</md-app-toolbar>

		<md-app-content>
			<md-empty-state
				md-icon=view_module
				md-label="Nothing in workspace"
				v-if="pages.length === 0">

				<md-button class="md-primary md-raised" @click=addFile>ADD NEW FILE</md-button>
			</md-empty-state>
			<draggable v-model=pages :options="{animation: 0}" v-else>
				<page
					class=page
					:page=p.pdf
					:name=p.name
					:pageNumber="p.num + 1"
					v-for="p in pages"
					:key=p.id
					@delete=deletePage(p) />
			</draggable>

			<md-button class="md-fab md-fab-bottom-right" @click=addFile>
				<md-icon>add</md-icon>
			</md-button>

			<md-dialog-alert
				:md-active.sync=loadError
				md-title="failed to load"
				md-content="filed to load this file. only PDF supported." />

			<md-dialog-alert
				:md-active.sync=serverError
				md-title="internal server error"
				md-content="sorry, an error occurred in the server. please retry later." />

			<input type=file ref=filepicker accept=.pdf @change=fileSelected>
		</md-app-content>
	</md-app>
</template>

<script>
import path from 'path';

import Vue from 'vue';
import {MdApp, MdToolbar, MdContent, MdEmptyState, MdButton, MdIcon, MdCard, MdProgress, MdDialog, MdDialogAlert} from 'vue-material/dist/components';
import 'vue-material/dist/vue-material.min.css';
import 'vue-material/dist/theme/default.css';

import PDFJS from 'pdfjs-dist';
import draggable from 'vuedraggable';
import axios from 'axios';

import Page from '~/components/Page.vue';
import AddFile from '~/components/AddFile.vue';


Vue.use(MdApp);
Vue.use(MdToolbar);
Vue.use(MdContent);
Vue.use(MdEmptyState);
Vue.use(MdButton);
Vue.use(MdIcon);
Vue.use(MdCard);
Vue.use(MdProgress);
Vue.use(MdDialog);
Vue.use(MdDialogAlert);


export default {
	components: {
		'draggable': draggable,
		'page': Page,
		'add-file': AddFile,
	},
	data() {
		return {
			pages: [],
			loadError: false,
			serverError: false,
		};
	},
	methods: {
		addFile() {
			this.$refs.filepicker.click();
		},
		fileSelected(ev) {
			const file = ev.target.files[0];
			if (!file) {
				return;
			}
			this.$refs.filepicker.value = '';

			if (file.type !== 'application/pdf') {
				this.loadError = true;
				return;
			}

			const reader = new FileReader();
			reader.onload = () => {
				this.loadPDF(path.basename(file.name), reader.result);
			};
			reader.onerror = () => {
				this.loadError = true;
			};
			reader.readAsDataURL(file);
		},
		loadPDF(name, uri) {
			PDFJS.getDocument(uri)
				.then(pdf => {
					const timestamp = new Date();

					for (let i=1; i<=pdf.numPages; i++) {
						this.pages.push({
							pdf: null,
							uri: uri,
							name: name,
							num: i-1,
							id: `${name}#${i-1}@${timestamp}`,
						});
						(id => {
							pdf.getPage(i).then(page => {
								for (let j=0; j<this.pages.length; j++) {
									if (this.pages[j].id === id) {
										this.pages[j].pdf = page;
										return;
									}
								}
							});
						})(`${name}#${i-1}@${timestamp}`);
					}
				})
		},
		deletePage(page) {
			this.pages = this.pages.filter(x => x.id != page.id);
		},
		save() {
			const keys = new Map();
			const files = new Map();
			const pages = [];

			let id = 0;
			this.pages.forEach(p => {
				if (keys.has(p.uri)) {
					pages.push({
						key: keys.get(p.uri),
						page: p.num,
					});
				} else {
					const key = id + '';
					id++;

					keys.set(p.uri, key);
					files.set(key, p.uri.substr(p.uri.indexOf(',') + 1));

					pages.push({
						key: key,
						page: p.num,
					});
				}
			});

			const fs = Array.from(files.entries())
							.map(([k, v]) => ({[k]: v}))
							.reduce((l, r) => Object.assign(l, r), {})

			axios.post('/', {files: fs, pages: pages})
				.then(resp => {
					if (resp.status === 200) {
						location.href = URL.createObjectURL(new Blob([resp.data], {type: 'application/pdf'}));
					} else {
						this.serverError = true;
					}
				})
				.catch(err => {
					console.error(err);
					this.serverError = true;
				})
		},
	},
};
</script>
