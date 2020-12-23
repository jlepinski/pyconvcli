import React, { Component } from 'react';


interface IOptionSelectionState {
    selected: string | null,
    values:any
  }

export class OptionSelection extends Component<{}, {}> {
   
    constructor(props:any){
        super(props)
        this.state.values=props.values?props.values:[]
        this.state.selected=props.selected?props.selected:null
    }

    public state: IOptionSelectionState = {
      selected: null,
      values:[]
    }
  
    public change(event:any) {
        return this.setState({selected:event.target.value})
    }
  
    public render() {
    
      return (
        <select onChange={this.change}>
            {this.state.values.map((value:any, index:number) => {
                return <option value="{value.name}">value.name</option>
            })}
        </select>
      );
    }
  }
  
  export default OptionSelection;
  