<template>
  <v-app>
    <v-app-bar flat color="grey-lighten-2" app class="appbar-custom"> <!-- 添加app属性解决遮挡问题 -->
      <v-toolbar-title>Kurocards wiki </v-toolbar-title>
      <v-spacer />
      <!-- 已移除API文本显示 -->
    </v-app-bar>
    
    <!-- 添加v-main包裹内容，解决导航栏遮挡问题 -->
    <v-main>
      <v-container fluid>
        <v-row>
          <!-- filters -->
          <v-col cols="3" md="2" class="filters-col">
            <v-card outlined class="filters-card" elevation="2">
              <v-card-text>
                <v-text-field v-model="q" label="关键词（名称/效果）" dense @input="onFilterDebounced" />
                <v-select :items="seriesOptions" v-model="filterSeries" label="系列" dense clearable />
                <v-select :items="rarityOptions" v-model="filterRarity" label="稀有度" dense clearable />
                
              <div class="my-2">类别（多选）</div>
                <!-- 一行 4 个的 Chip 容器 -->
                <div class="chip-container">
                  <v-chip
                    v-for="c in categoryOptions"
                    :key="c"
                    class="chip-item"
                    :color="selectedCats.includes(c) ? 'primary' : ''"
                    :text-color="selectedCats.includes(c) ? 'white' : ''"
                    outlined
                    @click="toggleChip(c)"
                  >
                    {{ c }}
                  </v-chip>
                </div>
                <v-row class="mt-3" dense>
                  <v-col cols="6">
                    <v-text-field v-model.number="minCost" label="费用 min" dense type="number" @input="onFilterDebounced" />
                  </v-col>
                  <v-col cols="6">
                    <v-text-field v-model.number="maxCost" label="费用 max" dense type="number" @input="onFilterDebounced" />
                  </v-col>
                </v-row>

                <v-row dense>
                  <v-col cols="6">
                    <!-- 标签改为“PP”，绑定变量改为ppValue -->
                    <v-text-field v-model.number="ppValue" label="PP" dense type="number" @input="onFilterDebounced" />
                  </v-col>
                  <v-col cols="6">
                    <!-- 标签改为“DP”，绑定变量改为dpValue -->
                    <v-text-field v-model.number="dpValue" label="DP" dense type="number" @input="onFilterDebounced" />
                  </v-col>
                </v-row>

                <v-row class="mt-4" dense>
                  <v-col cols="6">
                    <v-btn block @click="resetFilters" color="primary" text>重置</v-btn>
                  </v-col>
                  <v-col cols="6">
                    <v-btn block @click="exportJson" color="primary">导出JSON</v-btn>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>

          <!-- card grid -->
          <v-col cols="12" md="9">
            <v-row align="center" class="mb-2">
              <v-col>
                <div class="subtitle-1 grey--text">{{ filtered.length }} 张卡</div>
              </v-col>
              <v-col class="d-flex" cols="6" md="3">
              <v-select
                dense
                hide-details
                :items="sortOptions"
                v-model="sortBy"
                label="排序"
                item-title="label"
                item-value="value"
                @change="sortAndRender"
              />
              </v-col>
            </v-row>

            <v-row>
              <v-col v-for="card in filtered" :key="card.id" cols="3" sm="3" md="2" lg="2">
                <v-card class="hoverable" @click="open(card)" outlined>
                  <v-img :src="imageUrl(card)" height="auto" aspect-ratio="4/3" cover>
                    <template #placeholder>
                      <v-row class="fill-height ma-0" align="center" justify="center">
                        <v-progress-circular indeterminate color="grey lighten-1" />
                      </v-row>
                    </template>
                  </v-img>
                  <v-card-title class="text-no-wrap">{{ card.name }}</v-card-title>
                  <v-card-subtitle class="grey--text text--darken-1">
                    {{ card.id }} · {{ card.product_series || card.series }} · {{ card.rarity }}
                  </v-card-subtitle>
                  <v-card-text class="py-2">
                    <div class="caption">{{ card.category }}</div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
        <!-- Footer 声明区域 -->
        <div class="footer">
          <p class="footer-text">
            Kurocards 是一个非官方粉丝工具，所有卡牌资料版权归集卡社所有，
            本网站与集卡社并无任何官方合作或授权关系。
          </p>

          <p class="footer-text">
            © 2025 Kurocards. All rights reserved.
            <a href="mailto: sj-nick@foxmail.com" target="_blank" class="footer-link">｜问题反馈</a>
          </p>

          <div class="footer-dev">
            <v-icon class="footer-icon" size="20">mdi-github</v-icon>
            <span>Developed by </span>
            <a href="https://github.com/KuristNiaS" class="footer-link" target="_blank">KuristNiaS</a>
          </div>
        </div>
      </v-container>
    </v-main>

    <!-- modal -->
    <v-dialog v-model="dialog" max-width="900px">
      <v-card>
        <v-card-title>
          <span class="text-h6">{{ selectedCard?.name || selectedCard?.id }}</span>
          <v-spacer />
          <v-btn icon @click="dialog=false"><v-icon>mdi-close</v-icon></v-btn>
        </v-card-title>
        <v-card-text>
          <v-row>
            <v-col cols="12" md="5">
              <!-- 修复图片不显示问题，使用selectedCard -->
              <v-img 
              :src="imageUrl(selectedCard)" 
              aspect-ratio="450/629" 
              max-width="450"       
              cover
              ></v-img>
            </v-col>
            <v-col cols="12" md="7">
              <div><strong>ID:</strong> {{ selectedCard?.id }}</div>
              <div><strong>系列:</strong> {{ selectedCard?.product_series || selectedCard?.series }}</div>
              <div><strong>颜色:</strong> {{ selectedCard?.color }}</div>
              <div><strong>稀有度:</strong> {{ selectedCard?.rarity }}</div>
              <div><strong>类别:</strong> {{ selectedCard?.category }}</div>
              <div class="mt-2"><strong>效果:</strong>
                <div style="white-space:pre-wrap">{{ selectedCard?.eff }}</div>
              </div>
              <div 
                class="mt-2" 
                v-if="selectedCard?.category?.includes('角色')"  
              >
                <strong>费用 / PP / DP:</strong> {{ selectedCard?.cost }} / {{ selectedCard?.PP }} / {{ selectedCard?.DP }}
              </div>            
            </v-col>
          </v-row>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="dialog=false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

  </v-app>
</template>

<script>
import { computed, onMounted, ref } from 'vue';

/*
  配置：把 apiBase 和 imagesBase 改成你的地址
*/
const apiBase = 'https://pcg-fga3.onrender.com/api' // ← 改成后端地址
const imagesBase = 'https://pcg-wiki.vercel.app/images' // ← 改成图片目录 URL

export default {
  setup() {
    const all = ref([])
    const q = ref('')
    const filterSeries = ref('')
    const filterRarity = ref('')
    const selectedCats = ref([])
    const minCost = ref(null)
    const maxCost = ref(null)
    const ppValue = ref(null) // 精确匹配的PP值
    const dpValue = ref(null) // 精确匹配的DP值
    const sortBy = ref('id_asc')

    const dialog = ref(false)
    const selectedCard = ref(null)

  const sortOptions = [
    { label: 'ID ↑', value: 'id_asc' },
    { label: 'ID ↓', value: 'id_desc' },
    { label: '费用 ↑', value: 'cost_asc' },
    { label: '费用 ↓', value: 'cost_desc' },
    { label: '名称 ↑', value: 'name_asc' }
  ]

    const seriesOptions = ref([])
    const rarityOptions = ref([])
    const categoryOptions = ref([])

    const apiFetch = async () => {
      const candidates = [
        apiBase ? `${apiBase}/search` : null,
        apiBase ? `${apiBase}/cards` : null,
        '/cards.json'
      ].filter(Boolean)
      let data = []
      for (const url of candidates) {
        try {
          const r = await fetch(url)
          if (!r.ok) continue
          const j = await r.json()
          data = Array.isArray(j) ? j : (Array.isArray(j.cards) ? j.cards : [])
          break
        } catch(e){ /* try next */ }
      }
      // normalize
      all.value = data.map(normalize)
      // fill filter options
      seriesOptions.value = [...new Set(all.value.map(c=>c.product_series || c.series).filter(Boolean))].sort()
      rarityOptions.value = [...new Set(all.value.map(c=>c.rarity).filter(Boolean))].sort()
      categoryOptions.value = [...new Set(all.value.flatMap(c => (c.category||'').split('/').map(s=>s.trim()).filter(Boolean)))].sort()
    }

    onMounted(apiFetch)

    function normalize(raw){
      return {
        id: raw.id || raw.ID || raw.Id || raw.card_id || '',
        name: raw.name || raw.title || '',
        product_series: raw.product_series || raw.series || '',
        category: (raw.category || '').replace(/,/g, '/'),
        rarity: raw.rarity || raw.rank || '',
        color: raw.color || raw.colour || '',
        eff: raw.eff || raw.text || raw.description || '',
        cost: raw.cost !== undefined ? Number(raw.cost) : null,
        PP: raw.PP !== undefined ? Number(raw.PP) : null,
        DP: raw.DP !== undefined ? Number(raw.DP) : null
      }
    }

    // computed filtered list
    const filtered = computed(()=>{
      let list = all.value.slice()
      // keyword
      if (q.value) {
        const key = q.value.toLowerCase()
        list = list.filter(c => ((c.name||'') + ' ' + (c.eff||'')).toLowerCase().includes(key))
      }
      if (filterSeries.value) list = list.filter(c => (c.product_series||'') === filterSeries.value)
      if (filterRarity.value) list = list.filter(c => (c.rarity||'') === filterRarity.value)
      if (selectedCats.value.length) {
        list = list.filter(c => {
          const cardCats = (c.category||'').split('/').map(s=>s.trim()).filter(Boolean)
          return selectedCats.value.every(sel => cardCats.includes(sel))
        })
      }
      if (minCost.value !== null) list = list.filter(c => (c.cost || 0) >= minCost.value)
      if (maxCost.value !== null) list = list.filter(c => (c.cost || 0) <= maxCost.value)
      if (ppValue.value !== null) {
        // 仅保留PP值与输入完全相等的卡牌（处理null/undefined的情况）
        list = list.filter(c => (c.PP || null) === ppValue.value)
      }
      if (dpValue.value !== null) {
        // 仅保留DP值与输入完全相等的卡牌
        list = list.filter(c => (c.DP || null) === dpValue.value)
      }

      // sort
      const mode = sortBy.value
      list.sort((a,b)=>{
        if (mode === 'id_desc') return (b.id||'').localeCompare(a.id||'')
        if (mode === 'id_asc') return (a.id||'').localeCompare(b.id||'')
        if (mode === 'cost_asc') return (Number(a.cost)||0) - (Number(b.cost)||0)
        if (mode === 'cost_desc') return (Number(b.cost)||0) - (Number(a.cost)||0)
        if (mode === 'name_asc') return (a.name||'').localeCompare(b.name||'')
        return 0
      })
      return list
    })

    function imageUrl(card){
      const id = encodeURIComponent(card?.id || '')
      return `${imagesBase}/${id}.jpg`
    }

    function open(card){
      selectedCard.value = card
      dialog.value = true
    }

    function toggleChip(c){
      const idx = selectedCats.value.indexOf(c)
      if (idx >= 0) selectedCats.value.splice(idx,1)
      else selectedCats.value.push(c)
    }

    function resetFilters(){
      q.value = ''
      filterSeries.value = ''
      filterRarity.value = ''
      selectedCats.value = []
      minCost.value = null; maxCost.value = null; ppValue.value = null; dpValue.value = null
    }

    function exportJson(){
      const data = JSON.stringify(filtered.value, null, 2)
      const url = URL.createObjectURL(new Blob([data], {type:'application/json'}))
      const a = document.createElement('a'); a.href = url; a.download = 'cards_export.json'; a.click(); URL.revokeObjectURL(url)
    }

    // 修复防抖函数定义错误
    let t
    function onFilterDebounced(){
      clearTimeout(t); 
      t = setTimeout(()=>{
        // 触发过滤（计算属性会自动更新）
        console.log("过滤条件更新");
      }, 150)
    }

    function sortAndRender(){ /* reactive via computed */ }

    return {
      apiBase, imagesBase,
      q, filterSeries, filterRarity, minCost, maxCost, ppValue, dpValue, sortBy,
      seriesOptions, rarityOptions, categoryOptions, selectedCats,
      filtered, imageUrl, open, dialog, selectedCard, sortOptions,
      toggleChip, resetFilters, exportJson, onFilterDebounced
    }
  }
}
</script>



<style scoped>
.v-card { cursor: pointer; }

/* 芯片容器：flex + wrap */
.chip-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* 每行 4 个 */
.chip-item {
  flex: 0 0 calc(25% - 8px);
  justify-content: center;
  width: calc(25% - 8px);
}

/* 小屏幕：每行 2 个 */
@media (max-width: 600px) {
  .chip-item {
    flex: 0 0 calc(50% - 8px);
    width: calc(50% - 8px);
  }
}

.footer {
  margin-top: 40px;
  padding: 32px 0;
  text-align: center;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  line-height: 1.6;
}

.footer-text {
  margin: 4px 0;
}

.footer-dev {
  margin-top: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
}

.footer-link {
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
}

.footer-link:hover {
  text-decoration: underline;
}

.footer-icon {
  opacity: 0.8;
}

.v-application {
  background-color: #FAFAFA !important;
}

.filters-col {
  /* sticky 生效时要同时设置 align-self:start，确保列不会拉伸 */
  align-self: start;
  position: sticky;
  top: 64px;            /* 距离视口顶部 64px（通常 v-app-bar 高度）。根据实际 app-bar 高度调整 */
  z-index: 5;           /* 保证浮在内容之上但低于 dialog 等 */
  padding-top: 8px;     /* 视觉微调 */
}

/* 在小屏幕禁用 sticky（避免遮挡并更适配移动端） */
@media (max-width: 960px) {
  .filters-col {
    position: static;
    top: auto;
    z-index: auto;
  }
}
</style>

/* 2024 KuristNiaS 版权所有，遵循 MIT 许可证。 */