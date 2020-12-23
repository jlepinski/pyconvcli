import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import OptionSelection from './OptionSelection'
import * as _ from "lodash"

// Point Eel web socket to the instance
export const eel = window.eel
eel.set_host( 'ws://localhost:8080' )
let options = null



// allow logging to web app from the python base
function web_log(msg:string) {
  console.log(msg)
}
window.eel.expose(web_log, 'web_log')


interface IAppState {
  options:any
  selections:any
}

export class App extends Component<{}, {}> {
  constructor(props:any){
    super(props)
    this.state.options=JSON.parse('{"name": "test", "is_callable": false, "key": "test", "choices": [{"name": "here", "is_callable": false, "key": "test.here", "choices": [{"name": "custom", "is_callable": false, "key": "test.here.custom", "choices": [{"name": "groups", "is_callable": false, "key": "test.here.custom.groups", "choices": [{"name": "groupsCommand", "is_callable": true, "key": "test.here.custom.groups", "function_name": "groupsCommand", "form": {}}]}, {"name": "route", "is_callable": false, "key": "test.here.custom.route", "choices": [{"name": "commandOne", "is_callable": true, "key": "test.here.custom.route", "function_name": "commandOne", "form": {}}, {"name": "commandTwo", "is_callable": true, "key": "test.here.custom.route", "function_name": "commandTwo", "form": {}}]}]}]}]}')//eel.build_options()
    this.state.selections=[<OptionSelection selected="{state.options.name}" ></OptionSelection>]
  }
  public state: IAppState = {
    options: null,
    selections:null
  }
  public onSelectionChanged(option_selection:OptionSelection){
      const index = this.state.selections.index(option_selection)
      if(index==this.state.selections.length-1){
        options = _.find(option_selection.state.values, (child:any)=>child.name==option_selection.state.selected).choices
        this.state.selections.push(<OptionSelection options="{options}" ></OptionSelection>)
      }
  }

  public render() {
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <button>Copy to clip board</button>
          <button>Run Command</button>
          
        </header>
      </div>
    );
  }
}

export default App;
