<template>
  <v-app>
    <v-app-bar flat color="white">
      <v-toolbar-title>PCG 卡查 </v-toolbar-title>
      <v-spacer />
      <div class="text-subtitle-2 grey--text">API: {{ apiBase }}</div>
    </v-app-bar>1

    <v-container fluid>
      <v-row>
        <!-- filters -->
        <v-col cols="12" md="3">
          <v-card outlined>
            <v-card-text>
              <v-text-field v-model="q" label="关键词（名称/效果）" dense @input="onFilterDebounced" />
              <v-select :items="seriesOptions" v-model="filterSeries" label="系列" dense clearable />
              <v-select :items="rarityOptions" v-model="filterRarity" label="稀有度" dense clearable />
              
              <div class="my-2">类别（多选）</div>
              <div>
                <v-chip-group multiple column>
                  <v-chip
                    v-for="c in categoryOptions"
                    :key="c"
                    :value="c"
                    @click="toggleChip(c)"
                    :class="selectedCats.includes(c) ? 'primary white--text' : ''"
                    outlined
                    >
                    {{ c }}
                  </v-chip>
                </v-chip-group>
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
                  <v-text-field v-model.number="minPP" label="PP min" dense type="number" @input="onFilterDebounced" />
                </v-col>
                <v-col cols="6">
                  <v-text-field v-model.number="minDP" label="DP min" dense type="number" @input="onFilterDebounced" />
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
              <v-select dense hide-details :items="sortOptions" v-model="sortBy" label="排序" @change="sortAndRender" />
            </v-col>
          </v-row>

          <v-row>
            <v-col v-for="card in filtered" :key="card.id" cols="12" sm="6" md="4" lg="3">
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
    </v-container>

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
              <v-img 
              :src="imageUrl(card)" 
              aspect-ratio="450/629"  <!-- 精确比例 -->
              max-width="450"         <!-- 限制最大宽度 -->
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
              <div class="mt-2"><strong>费用 / PP / DP:</strong> {{ selectedCard?.cost }} / {{ selectedCard?.PP }} / {{ selectedCard?.DP }}</div>
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

//test

export default {
  setup() {
    const all = ref([])
    const q = ref('')
    const filterSeries = ref('')
    const filterRarity = ref('')
    const selectedCats = ref([])
    const minCost = ref(null)
    const maxCost = ref(null)
    const minPP = ref(null)
    const minDP = ref(null)
    const sortBy = ref('id_desc')

    const dialog = ref(false)
    const selectedCard = ref(null)

    const sortOptions = [
      { label: 'ID ↓', value: 'id_desc' },
      { label: 'ID ↑', value: 'id_asc' },
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
      if (minPP.value !== null) list = list.filter(c => (c.PP || 0) >= minPP.value)
      if (minDP.value !== null) list = list.filter(c => (c.DP || 0) >= minDP.value)

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
      minCost.value = null; maxCost.value = null; minPP.value = null; minDP.value = null
    }

    function exportJson(){
      const data = JSON.stringify(filtered.value, null, 2)
      const url = URL.createObjectURL(new Blob([data], {type:'application/json'}))
      const a = document.createElement('a'); a.href = url; a.download = 'cards_export.json'; a.click(); URL.revokeObjectURL(url)
    }

    // debounce for input
    let t
    function onFilterDebounced(){
      function onFilterDebounced(){
      clearTimeout(t); 
      t = setTimeout(()=>{
    // 触发过滤（计算属性会自动更新，这里可加日志或调试信息）
      console.log("过滤条件更新");
      }, 150)
    }
    }

    function sortAndRender(){ /* reactive via computed */ }

    return {
      apiBase, imagesBase,
      q, filterSeries, filterRarity, minCost, maxCost, minPP, minDP, sortBy,
      seriesOptions, rarityOptions, categoryOptions, selectedCats,
      filtered, imageUrl, open, dialog, selectedCard, sortOptions,
      toggleChip, resetFilters, exportJson, onFilterDebounced
    }
  }
}
</script>

<style scoped>
.v-card { cursor: pointer; }
</style>
