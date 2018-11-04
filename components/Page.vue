<template>
	<md-card>
		<md-card-media-cover md-solid>
			<md-card-media ref=wrapper>
				<md-progress-spinner md-mode=indeterminate />
			</md-card-media>

			<md-card-area>
				<md-card-header>
					<div class=md-title>{{ name }}</div>
					<div class=md-subhead>page: {{ pageNumber }}</div>
				</md-card-header>

				<md-card-actions>
					<md-button class=md-icon-button @click="$emit('delete')">
						<md-icon>delete</md-icon>
					</md-button>
				</md-card-actions>
			</md-card-area>
		</md-card-media-cover>
	</md-card>
</template>

<script>
import PDFJS from 'pdfjs-dist';


export default {
	props: ['page', 'name', 'pageNumber'],

	mounted() {
		this.load();
	},
	watch: {
		page() {
			this.load();
		},
	},
	methods: {
		load() {
		if (this.page !== null) {
			this.page.getOperatorList()
				.then(opList => (new PDFJS.SVGGraphics(this.page.commonObjs, this.page.objs)).getSVG(opList, this.page.getViewport(0.5)))
				.then(svg => {
					const target = this.$refs.wrapper.$el;
					target.removeChild(target.firstChild);
					target.appendChild(svg);
				});
		}
		},
	},
};
</script>
