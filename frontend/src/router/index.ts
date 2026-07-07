import { createRouter, createWebHistory } from "vue-router";
import MarketView from "../views/MarketView.vue";
import BankProjectsView from "../views/BankProjectsView.vue";
import BankRecognitionView from "../views/BankRecognitionView.vue";
import BankReportView from "../views/BankReportView.vue";
import RegulationsView from "../views/RegulationsView.vue";
import DocumentDiffView from "../views/DocumentDiffView.vue";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", redirect: "/market" },
    { path: "/market", component: MarketView },
    { path: "/bank/projects", component: BankProjectsView },
    { path: "/bank/projects/:id/recognition", component: BankRecognitionView },
    { path: "/bank/projects/:id/report", component: BankReportView },
    { path: "/regulations", component: RegulationsView },
    { path: "/document-diff", component: DocumentDiffView }
  ]
});

export default router;
