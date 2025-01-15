<template>
  <div class="table-main">
    <div
      v-for="(row, index) in arrData"
      :key="index"
      class="row-data m-2 d-flex"
    >
      <div class="key p-2 d-inline-block" style="">
        <div class="text-capitalize ">
          {{ keyTitle(row) }} <span v-if="showDataType">({{ checkValueType(data[row]) }})</span>
        </div>
        <div v-if="showKey" style="font-family: monospace;">key: {{row}}</div>
      </div>
      <div class="value" v-if="['string', 'number'].includes(checkValueType(data[row]))">
        <div class="p-2 d-inline-block">{{ data[row] }}</div>
      </div>
      <div class="value" v-else-if="checkValueType(data[row]) === 'array'">
        <div v-for="(arrRow, index2) in data[row]" :key="index2" class="d-flex">
          <div class="mx-2">--</div>
          <div v-if="['string', 'number'].includes(checkValueType(arrRow))">
            {{ arrRow }}
          </div>
          <div v-else>
            <JsonToHtmlTable :data="arrRow" />
          </div>
        </div>
      </div>
      <div class="value" v-else>
        <JsonToHtmlTable :data="data[row]" />
      </div>
    </div>
  </div>
</template>
  
<script>
export default {
  name: "JsonToHtmlTable",
  props: {
    data: {
      type: Object,
    }
  },
  data() {
    return {
      showDataType: false,
      showKey: false
    }
  },
  computed: {
    arrData() {
      if (this.data == null) {
        return "";
      }
      return Object.keys(this.data);
    }
  },
  methods: {
    keyTitle(key) {
      // JavaScript escape code for nbsp: \xa0
      return key.split("_").join(" ").replace(" ", "\xa0");
    },
    checkValueType(val) {
      if (typeof val !== "object") {
        return typeof val;
      }
      return Array.isArray(val) ? "array" : "object";
    }
  }
};
</script>
  
<style scoped>

.table-main {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.m-2 {
  margin: .2rem 0 .2rem 0!important;
}

.mx-2 {
  margin-right: .5rem!important;
}

.p-2 {
  padding: .5rem!important;
}

.d-flex {
  display: flex!important;
}

.d-inline-block {
  display: inline-block!important;
}

.text-capitalize {
  text-transform: capitalize!important;
}

.key {
  width: 20%;
  background: lightgray;
}

.value {
  width: 80%;
}

.table-main  .row-data {
  border: 2px solid lightgrey;
  border-radius: 2px;
}
</style>